from typing import List
from fastapi import APIRouter, Depends, HTTPException,  File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.cruds.files import post_files

router = APIRouter(prefix="/files")


# 公式ドキュメント参照
@router.post("/upload", response_model=dict)
async def upload_files(files: List[UploadFile] = File(...)) -> dict:
    # ファイルをGoogle Cloud Storageにアップロード
    upload_result = await post_files(files)
    
    if "success" not in upload_result or not upload_result["success"]:
        raise HTTPException(status_code=500, detail="ファイルのアップロードに失敗しました")
    
    return upload_result