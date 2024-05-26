from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException,  File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.cruds.files import create_file, post_files, post_filename_to_db
from app.schemas.files import FileCreate
from app.db import get_db

router = APIRouter(prefix="/files/", tags=["files"])

# 公式ドキュメント参照
@router.post("/upload", response_model=FileCreate)
async def upload_file(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    try:
        # ファイルをGoogle Cloud Storageにアップロード
        await post_files(file)

        # アップロードしたファイルの情報をデータベースに保存
        db_file = await post_filename_to_db(db, file)

        return FileCreate(file_name=db_file.file_name, file_path=db_file.file_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))