from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException,  File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.cruds.files import post_files
from app.schemas.files import FileCreate
from app.db import get_db

router = APIRouter(prefix="/files")


# 公式ドキュメント参照
@router.post("/upload", response_model=dict)
async def upload_files(files: List[UploadFile] = File(...), db: AsyncSession = Depends(get_db)) -> dict:
    try:
        # ファイルをGoogle Cloud Storageにアップロードし、データベースに保存
        return await post_files(files, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))