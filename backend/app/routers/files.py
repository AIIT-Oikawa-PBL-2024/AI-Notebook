from fastapi import APIRouter, HTTPException, File, UploadFile
from app.cruds.files import post_files
from typing import List

router = APIRouter(prefix="/files")


# 公式ドキュメント参照
@router.post("/upload", response_model=dict)
async def upload_files(files: List[UploadFile] = None) -> dict:
    if files is None:
        files = File(...)
    # ファイルをGoogle Cloud Storageにアップロード
    upload_result = await post_files(files)
    
    if "success" not in upload_result or not upload_result["success"]:
        raise HTTPException(status_code=500, detail="Upload failed")
    
    return {"success": upload_result.get("success", False)}