import logging
import unicodedata
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

import app.cruds.files as files_cruds
import app.schemas.files as files_schemas
from app.database import get_db
from app.utils.operate_cloud_storage import delete_files_from_gcs, post_files
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
    upload_result = await post_files(files)

    if "success" not in upload_result or not upload_result["success"]:
        raise HTTPException(status_code=500, detail="Upload failed")

    for file in files:
        if file.filename and file.size:
            # ファイル名を正規化
            normalized_filename = unicodedata.normalize("NFC", file.filename)

            # 日本時間の現在日時を取得
            now_japan = datetime.now(JST)

            file_create = files_schemas.FileCreate(
                file_name=normalized_filename,
                file_size=file.size,
                user_id=uid,
                created_at=now_japan,
            )

            # ファイル情報を保存
            try:
                regist_file = await files_cruds.create_file(db, file_create, uid)
                logging.info(f"File {regist_file.file_name} saved to database.")
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
    """
    try:
        # ファイルをDBから削除
        for file_name in files:
            await files_cruds.delete_file_by_name_and_userid(db, file_name, uid)

        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"{file_name} ファイルの削除に失敗しました",
        ) from e

    # ファイルをGoogle Cloud Storageから削除
    response_data = {}
    delete_result = await delete_files_from_gcs(files)

    response_data["success"] = delete_result.get("success", False)
    response_data["success_files"] = delete_result.get("success_files", [])
    response_data["failed_files"] = delete_result.get("failed_files", [])
    return response_data
