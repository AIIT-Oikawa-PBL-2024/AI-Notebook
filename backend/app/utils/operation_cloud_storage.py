import io
import os
from dotenv import load_dotenv
from typing import List
from fastapi import UploadFile, HTTPException
from google.cloud import storage
from google.oauth2 import service_account
from google.cloud import exceptions as google_exceptions

# 環境変数を読み込む
load_dotenv()

# 環境変数から認証情報取得
service_account_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
credentials = service_account.Credentials.from_service_account_file(service_account_credentials_path)

# ファイルを読み込む関数
async def post_files(files: List[UploadFile]) -> dict:
    allowed_extensions = [".png", ".pdf", ".jpeg", ".jpg"]
    ext_correct_files, ext_error_files = [],[]

    for file in files:
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            ext_error_files.append(file.filename)
        else:
            ext_correct_files.append(file)

    if ext_error_files:
        raise HTTPException(
            status_code=400, detail=f"アップロード対象外の拡張子です。{', '.join(ext_error_files)}"
            )
    # ファイルのアップロード処理
    upload_result = await upload_files(ext_correct_files)

    if "success" not in upload_result or not upload_result["success"]:
        raise HTTPException(status_code=500, detail="ファイルのアップロードに失敗しました")

    return upload_result

async def upload_files(ext_correct_files: List[UploadFile]) -> dict:
    success_files, failed_files = [], []  # アップロードに失敗したファイル

    for file in ext_correct_files:
        bucket_name = os.getenv("GCS_BUCKET_NAME")
        client = storage.Client(credentials=credentials)
        bucket = client.bucket(bucket_name)
        file_content = await file.read()
        file_obj = io.BytesIO(file_content)
        destination_blob_name = file.filename
        blob = bucket.blob(destination_blob_name)
        file_obj.seek(0)
        try:
            # アップロードの実行
            blob.upload_from_file(file_obj)

            # アップロードの結果をチェック
            if blob.exists():
                success_message = f"ファイル {file.filename} のアップロードが成功しました"
                success_files.append(
                    {"message": success_message, "filename": file.filename}
                    )
            else:
                error_message = f"ファイル {file.filename} のアップロードに失敗しました"
                failed_files.append(error_message)

        # except exceptions.GoogleCloudError as e:
        except google_exceptions.GoogleCloudError as e:
            error_message = f"ファイル {file.filename} のアップロード中にエラーが発生しました: {str(e)}"
            failed_files.append(error_message)

        except Exception as e:
            error_message = f"ファイル {file.filename} のアップロード中に予期しないエラーが発生しました: {str(e)}"
            failed_files.append(error_message)

    if failed_files:
        error_details = "\n".join(failed_files)
        return {"success": False, "success_files": success_files, "failed_files": error_details}

    return {"success": True, "success_files": success_files}