import logging
import unicodedata
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

import app.cruds.files as files_cruds
import app.schemas.files as files_schemas
from app.cruds.files import get_file_id_by_name_and_userid
from app.database import get_db
from app.utils.operate_cloud_storage import (
    delete_files_from_gcs,
    generate_upload_signed_url_v4,
    post_files,
)
from app.utils.user_auth import get_uid

# 環境変数を読み込む
load_dotenv()

# ロギング設定
logging.basicConfig(level=logging.INFO)

# ルーターの設定
router = APIRouter(
    prefix="/files",
    tags=["files"],
)

# 日本時間のタイムゾーン
JST = timezone(timedelta(hours=9))

# 依存関係
db_dependency = Depends(get_db)


# GCSへのファイルアップロードとファイル名をDBに登録
@router.post("/upload", response_model=dict)
async def upload_files(
    files: list[UploadFile],
    db: AsyncSession = db_dependency,
    uid: str = Depends(get_uid),
) -> dict:
    """
    ファイルをGoogle Cloud Storageにアップロードし、ファイル名をDBに登録します。

    :param files: アップロードするファイルのリスト
    :type files: list[UploadFile]
    :param db: データベースセッション
    :type db: AsyncSession
    :param uid: ユーザーID
    :type uid: str
    :return: アップロード結果の辞書
    :rtype: dict
    :raises HTTPException: アップロードまたはデータベース登録に失敗した場合
    """
    response_data = {}

    # ファイルをGoogle Cloud Storageにアップロード
    upload_result = await post_files(files, uid)

    if "success" not in upload_result or not upload_result["success"]:
        raise HTTPException(status_code=500, detail="Upload failed")

    for file in files:
        if file.filename and file.size:
            # ファイル名を正規化
            normalized_filename = unicodedata.normalize("NFC", file.filename)
            # 日本時間の現在日時を取得
            now_japan = datetime.now(JST)

            # ファイル情報を保存
            try:
                file_id = await get_file_id_by_name_and_userid(db, normalized_filename, uid)
                if file_id is None:
                    logging.info(f"File {normalized_filename} not found in database.")
                    file_create = files_schemas.FileCreate(
                        file_name=normalized_filename,
                        file_size=file.size,
                        user_id=uid,
                        created_at=now_japan,  # 日本時間の現在日時を設定
                        updated_at=now_japan,  # 日本時間の現在日時を設定
                    )
                    regist_file = await files_cruds.create_file(db, file_create, uid)
                    logging.info(f"File {regist_file.file_name} saved to database.")
                else:
                    logging.info(f"File {normalized_filename} found in database. {file_id}")
                    file_update = files_schemas.FileUpdate(
                        file_name=normalized_filename,
                        file_size=file.size,
                        user_id=uid,
                        updated_at=now_japan,  # 日本時間の現在日時を設定
                    )
                    print(file_id)
                    update_file = await files_cruds.update_file(db, file_id, file_update, uid)
                    if update_file:
                        logging.info(f"File {update_file.file_name} updated in database.")
                    else:
                        logging.error(f"Failed to update file {normalized_filename} in database.")
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"{file.filename} データベース登録に失敗しました",
                ) from e

    response_data["success"] = upload_result.get("success", False)
    response_data["success_files"] = upload_result.get("success_files", [])
    response_data["failed_files"] = upload_result.get("failed_files", [])
    return response_data


# ファイルの一覧取得
@router.get("/", response_model=list[files_schemas.File])
async def get_files(
    db: AsyncSession = db_dependency, uid: str = Depends(get_uid)
) -> list[files_schemas.File]:
    """
    データベースからファイルの一覧を取得します。

    :param db: データベースセッション
    :type db: AsyncSession
    :param uid: ユーザーID
    :type uid: str
    :return: ファイルのリスト
    :rtype: list[files_schemas.File]
    """
    return await files_cruds.get_files_by_user_id(db, uid)


# ファイルの取得
@router.get("/{file_id}", response_model=files_schemas.File)
async def get_file_by_id(
    file_id: int, db: AsyncSession = db_dependency, uid: str = Depends(get_uid)
) -> files_schemas.File:
    """
    指定されたIDのファイルをデータベースから取得します。

    :param file_id: ファイルのID
    :type file_id: int
    :param db: データベースセッション
    :type db: AsyncSession
    :param uid: ユーザーID
    :type uid: str
    :return: ファイル情報
    :rtype: files_schemas.File
    :raises HTTPException: ファイルが見つからない場合
    """
    file = await files_cruds.get_file_by_id_and_user_id(db, file_id, uid)
    if not file:
        raise HTTPException(status_code=404, detail="ファイルが見つかりません")
    return file


# ファイル名のリストとユーザーIDによるファイルの削除
@router.delete("/delete_files", response_model=dict)
async def delete_files(
    files: list[str], db: AsyncSession = db_dependency, uid: str = Depends(get_uid)
) -> dict:
    """
    ファイルを削除するAPIエンドポイントです。

    :param files: 削除するファイルのリスト
    :type files: list[str]
    :param db: データベースセッション
    :type db: AsyncSession
    :param uid: ユーザーID
    :type uid: str
    :return: 削除結果の辞書
    :rtype: dict
    :raises HTTPException: ファイルが見つからない場合は404、その他のエラーは500を返します
    """
    response_data = {}

    try:
        # Google Cloud Storageからファイルを削除
        delete_result = await delete_files_from_gcs(files, uid)
        response_data.update(delete_result)

        # ファイルが見つからない場合は404エラーを返す
        if not delete_result.get("success", False) and "が存在しません" in delete_result.get(
            "failed_files", ""
        ):
            raise HTTPException(
                status_code=404,
                detail=delete_result["failed_files"],
            )

        # GCSでの削除が成功した場合のみ、DBからの削除を実行
        if delete_result.get("success", False):
            try:
                # ファイルをDBから削除
                for file_name in files:
                    await files_cruds.delete_file_by_name_and_userid(db, file_name, uid)
                await db.commit()

            except Exception as e:
                # DB削除でエラーが発生した場合
                await db.rollback()
                logging.error(f"DB削除エラー: {str(e)}", exc_info=True)
                # レスポンスを更新して失敗を反映
                response_data["success"] = False
                if "failed_files" in response_data:
                    if isinstance(response_data["failed_files"], list):
                        response_data["failed_files"].append(f"DBエラー: {str(e)}")
                    else:
                        response_data["failed_files"] = [
                            response_data["failed_files"],
                            f"DBエラー: {str(e)}",
                        ]
                else:
                    response_data["failed_files"] = [f"DBエラー: {str(e)}"]

        return response_data

    except HTTPException:
        # 404エラーの再送出
        raise

    except Exception as e:
        # その他のエラー（GCS削除エラーなど）
        logging.error(f"ファイル削除エラー: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"ファイル削除中にエラーが発生しました: {str(e)}",
        ) from e


# 署名付きURLの生成
@router.post("/generate_upload_signed_url", response_model=dict)
async def generate_upload_signed_url(files: list[str], uid: str = Depends(get_uid)) -> dict:
    """
    指定されたファイルリストに対してアップロード用の署名付きURLを生成します。

    :param files: 署名付きURLを生成するファイルのリスト
    :type files: list[str]
    :raises HTTPException: URL生成中にエラーが発生した場合、
    ステータスコード500とエラーメッセージを含むHTTPExceptionを送出します。
    :return: ファイル名をキーとし、署名付きURLを値とする辞書
    :rtype: dict
    """
    try:
        upload_signed_urls: dict[str, str] = {}
        upload_signed_urls = await generate_upload_signed_url_v4(files, uid)
        return upload_signed_urls

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# 署名付きURLでアップロードしたファイルのDB登録
@router.post("/register_files", response_model=bool)
async def register_files(
    files: list[UploadFile],
    db: AsyncSession = db_dependency,
    uid: str = Depends(get_uid),
) -> bool:
    """
    署名付きURLでアップロードしたファイルの情報をDBに登録します。

    :param files: アップロードしたファイルのリスト
    :type files: list[UploadFile]
    :param db: データベースセッション
    :type db: AsyncSession
    :return: 登録結果の辞書
    :rtype: bool
    """
    for file in files:
        if file.filename and file.size:
            # ファイル名を正規化
            normalized_filename = unicodedata.normalize("NFC", file.filename)
            # 日本時間の現在日時を取得
            now_japan = datetime.now(JST)

            # ファイル情報を保存
            try:
                file_id = await get_file_id_by_name_and_userid(db, normalized_filename, uid)
                if file_id is None:
                    logging.info(f"File {normalized_filename} not found in database.")
                    file_create = files_schemas.FileCreate(
                        file_name=normalized_filename,
                        file_size=file.size,
                        user_id=uid,
                        created_at=now_japan,  # 日本時間の現在日時を設定
                        updated_at=now_japan,  # 日本時間の現在日時を設定
                    )
                    regist_file = await files_cruds.create_file(db, file_create, uid)
                    logging.info(f"File {regist_file.file_name} saved to database.")
                else:
                    logging.info(f"File {normalized_filename} found in database. {file_id}")
                    file_update = files_schemas.FileUpdate(
                        file_name=normalized_filename,
                        file_size=file.size,
                        user_id=uid,
                        updated_at=now_japan,  # 日本時間の現在日時を設定
                    )
                    print(file_id)
                    update_file = await files_cruds.update_file(db, file_id, file_update, uid)
                    if update_file:
                        logging.info(f"File {update_file.file_name} updated in database.")
                    else:
                        logging.error(f"Failed to update file {normalized_filename} in database.")
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"{file_create.file_name} データベース登録に失敗しました",
                ) from e
                return False
    return True
