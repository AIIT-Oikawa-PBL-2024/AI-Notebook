import logging
import unicodedata
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

import app.cruds.files as files_cruds
import app.schemas.files as files_schemas
from app.database import get_db
from app.utils.operate_cloud_storage import post_files

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
) -> dict:
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
                user_id=1,  # ユーザIDは仮で1を設定
                created_at=now_japan,  # 日本時間の現在日時を設定
            )

            # ファイル情報を保存
            try:
                regist_file = await files_cruds.create_file(db, file_create)
                logging.info(f"File {regist_file.file_name} saved to database.")
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"{regist_file.file_name} データベース登録に失敗しました",
                ) from e

    response_data["success"] = upload_result.get("success", False)
    response_data["success_files"] = upload_result.get("success_files", [])
    response_data["failed_files"] = upload_result.get("failed_files", [])
    return response_data


# ファイルの一覧取得
@router.get("/", response_model=list[files_schemas.File])
async def get_files(db: AsyncSession = db_dependency) -> list[files_schemas.File]:
    return await files_cruds.get_files(db)


# ファイルの取得
@router.get("/{file_id}", response_model=files_schemas.File)
async def get_file_by_id(
    file_id: int, db: AsyncSession = db_dependency
) -> files_schemas.File:
    file = await files_cruds.get_file_by_id(db, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="ファイルが見つかりません")
    return file


# ファイルの削除
@router.delete("/{file_id}", response_model=dict)
async def delete_file(file_id: int, db: AsyncSession = db_dependency) -> dict:
    file = await files_cruds.get_file_by_id(db, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="ファイルが見つかりません")
    await files_cruds.delete_file(db, file)
    return {"detail": "ファイルが削除されました"}
