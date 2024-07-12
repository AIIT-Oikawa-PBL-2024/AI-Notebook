import io
import logging
import os
import unicodedata

from dotenv import load_dotenv
from fastapi import HTTPException, UploadFile
from google.api_core.exceptions import GoogleAPIError
from google.cloud import storage

# 環境変数を読み込む
load_dotenv()


# ファイルを読み込む関数
async def post_files(files: list[UploadFile]) -> dict:
    allowed_extensions = [".png", ".pdf", ".jpeg", ".jpg"]
    ext_correct_files, ext_error_files = [], []

    for file in files:
        # filenameがNoneでないことを確認
        if file.filename:
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension not in allowed_extensions:
                ext_error_files.append(file.filename)
            else:
                ext_correct_files.append(file)

    # ファイルのアップロード処理
    upload_result = await upload_files(ext_correct_files)

    if "success" not in upload_result or not upload_result["success"]:
        raise HTTPException(
            status_code=500, detail="ファイルのアップロードに失敗しました"
        )

    if ext_error_files:
        raise HTTPException(
            status_code=400,
            detail=f"アップロード対象外の拡張子です。{', '.join(ext_error_files)}",
        )

    return upload_result


async def upload_files(ext_correct_files: list[UploadFile]) -> dict:
    success_files, failed_files = [], []  # アップロードに失敗したファイル

    # 環境変数から認証情報を取得
    credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    bucket_name = os.getenv("BUCKET_NAME")

    for file in ext_correct_files:
        # ブロブ名を正規化
        if file.filename:
            normalized_blobname = unicodedata.normalize("NFC", file.filename)

        client = storage.Client.from_service_account_json(credentials)
        bucket = storage.Bucket(client, bucket_name)
        file_content = await file.read()
        file_obj = io.BytesIO(file_content)
        destination_blob_name = normalized_blobname
        blob = bucket.blob(destination_blob_name)
        file_obj.seek(0)
        try:
            # アップロードの実行
            blob.upload_from_file(file_obj)

            # アップロードの結果をチェック
            if blob.exists():
                success_message = (
                    f"ファイル {file.filename} のアップロードが成功しました"
                )
                success_files.append(
                    {"message": success_message, "filename": file.filename}
                )
            else:
                error_message = f"ファイル {file.filename} のアップロードに失敗しました"
                failed_files.append(error_message)

        # Google Cloud に関連するエラーの処理
        except GoogleAPIError as e:
            error_msg_part = (
                f"ファイル {file.filename} のアップロード中にエラーが発生しました: "
            )
            error_message = error_msg_part + str(e)
            failed_files.append(error_message)

        # その他一般的なエラーの処理
        except Exception as e:
            base_msg = "ファイルのアップロード中に予期しないエラーが発生しました: "
            error_detail = str(e)
            filename_msg = f"{file.filename} "
            error_message = filename_msg + base_msg + error_detail
            failed_files.append(error_message)

    if failed_files:
        error_details = "\n".join(failed_files)
        return {
            "success": False,
            "success_files": success_files,
            "failed_files": error_details,
        }

    return {"success": True, "success_files": success_files}


async def delete_files_from_gcs(files: list[str]) -> dict:
    """
    Google Cloud Storageからファイルを削除する

    :param files: 削除するファイルのリスト
    :type files: list[str]
    :return: 削除の結果を示す辞書
    :rtype: dict
    """
    success_files, failed_files = [], []

    # 環境変数から認証情報を取得
    credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    bucket_name = os.getenv("BUCKET_NAME")

    client = storage.Client.from_service_account_json(credentials)
    bucket = storage.Bucket(client, bucket_name)

    for filename in files:
        # ブロブ名を正規化
        normalized_blobname = unicodedata.normalize("NFC", filename)
        blob = bucket.blob(normalized_blobname)

        try:
            blob.delete()
            success_message = f"ファイル {normalized_blobname} が削除されました"
            success_files.append(
                {"message": success_message, "filename": normalized_blobname}
            )
        except GoogleAPIError as e:
            error_msg_part = (
                f"ファイル {normalized_blobname} の削除中にエラーが発生しました: "
            )
            error_message = error_msg_part + str(e)
            failed_files.append(error_message)
            logging.error(error_message)
        except Exception as e:
            base_msg = "ファイルの削除中に予期しないエラーが発生しました: "
            error_detail = str(e)
            filename_msg = f"{normalized_blobname} "
            error_message = filename_msg + base_msg + error_detail
            failed_files.append(error_message)
            logging.error(error_message)

    if failed_files:
        error_details = "\n".join(failed_files)
        return {
            "success": False,
            "success_files": success_files,
            "failed_files": error_details,
        }

    return {"success": True, "success_files": success_files}
