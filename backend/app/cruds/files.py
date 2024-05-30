from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import io
import logging
import os
import app.models.files as file_models
import app.schemas.files as files_schemas
from google.cloud import storage
from google.oauth2 import service_account
from fastapi import FastAPI, File, UploadFile, HTTPException, Response
from typing import List
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

# 環境変数から認証情報取得
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
credentials = service_account.Credentials.from_service_account_file(credentials_path)

async def post_files(files: List[UploadFile], db: AsyncSession) -> dict:
    allowed_extensions = [".png", ".pdf", ".jpeg", ".jpg"]
    success_files = []  # アップロード成功ファイル
    failed_files = []  # アップロード失敗ファイル
    
    #  オブジェクトアップロード処理
    try:
        bucket_name = os.getenv("GCS_BUCKET_NAME")
        client = storage.Client(credentials=credentials)
        bucket = client.bucket(bucket_name)
        upload_tasks = []
        for file in files:
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension not in allowed_extensions:
                failed_files.append({"filename": file.filename, "reason": "拡張子が許可されていません"})
                continue #拡張子が許可されている場合は下記の処理に続く

            file_content = await file.read()
            file_obj = io.BytesIO(file_content)
            destination_blob_name = file.filename
            blob = bucket.blob(destination_blob_name)
            file_obj.seek(0)

            try:
                upload_result = await blob.upload_from_file(file_obj)
                upload_tasks.append((file, upload_result))
            except Exception as e:
                failed_files.append({"filename": file.filename, "reason": str(e)})

        if not upload_tasks:
            return {
                "message": "ファイルアップロードが完了しました。",
                "success_files": success_files,
                "failed_files": failed_files,
            }

        for file, result in upload_tasks:
            if isinstance(result, Exception):
                failed_files.append({"filename": file.filename, "reason": str(result)})
            else:
                success_files.append(file.filename)
                logging.info(f"Stream data uploaded to {file.filename} in bucket {bucket_name}.")
                db_file = file_models.File(file_name=file.filename)
                db.add(db_file)
                await db.commit()
                await db.refresh(db_file)

        return {
            "message": "ファイルアップロードが完了しました。",
            "success_files": success_files,
            "failed_files": failed_files,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))