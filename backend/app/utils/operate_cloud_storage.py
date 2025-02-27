import asyncio
import datetime
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
async def post_files(files: list[UploadFile], uid: str) -> dict:
    """
    アップロードされたファイルを処理し、
    Google Cloud Storageにアップロードするエンドポイント

    :param files: アップロードされたファイルのリスト
    :type files: list[UploadFile]
    :return: アップロード結果を含む辞書
    :rtype: dict
    :raises HTTPException: ファイルの拡張子が無効な場合や、アップロードに失敗した場合
    """
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
    upload_result = await upload_files(ext_correct_files, uid)

    if "success" not in upload_result or not upload_result["success"]:
        raise HTTPException(status_code=500, detail="ファイルのアップロードに失敗しました")

    if ext_error_files:
        raise HTTPException(
            status_code=400,
            detail=f"アップロード対象外の拡張子です。{', '.join(ext_error_files)}",
        )

    return upload_result


async def upload_files(ext_correct_files: list[UploadFile], uid: str) -> dict:
    """
    ファイルをGoogle Cloud Storageにアップロードする

    :param ext_correct_files: アップロードする正しい拡張子を持つファイルのリスト
    :type ext_correct_files: list[UploadFile]
    :return: アップロード結果を含む辞書
    :rtype: dict
    """
    success_files, failed_files = [], []  # アップロードに失敗したファイル

    # 環境変数から認証情報を取得
    credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    bucket_name = os.getenv("BUCKET_NAME")

    for file in ext_correct_files:
        # ブロブ名を正規化
        if file.filename:
            # ユーザーIDの検証
            if not uid or not uid.strip():
                raise ValueError("Invalid user ID")

            # パスの正規化
            safe_uid = uid.strip().rstrip("/")
            normalized_blobname = unicodedata.normalize("NFC", f"{safe_uid}/{file.filename}")

        client = storage.Client.from_service_account_json(credentials)
        bucket = storage.Bucket(client, bucket_name)
        file_content = await file.read()
        file_obj = io.BytesIO(file_content)
        destination_blob_name = normalized_blobname
        blob = bucket.blob(destination_blob_name)
        file_obj.seek(0)
        try:
            # アップロードの実行
            await asyncio.to_thread(blob.upload_from_file, file_obj)

            # アップロードの結果をチェック
            exists = await asyncio.to_thread(blob.exists)
            if exists:
                success_message = f"ファイル {file.filename} のアップロードが成功しました"
                success_files.append({"message": success_message, "filename": file.filename})
            else:
                error_message = f"ファイル {file.filename} のアップロードに失敗しました"
                failed_files.append(error_message)

        # Google Cloud に関連するエラーの処理
        except GoogleAPIError as e:
            error_msg_part = f"ファイル {file.filename} のアップロード中にエラーが発生しました: "
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


async def delete_files_from_gcs(files: list[str], uid: str) -> dict:
    """
    Google Cloud Storageからファイルを削除します。
    """
    success_files, failed_files = [], []

    credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    bucket_name = os.getenv("BUCKET_NAME")

    if not credentials or not bucket_name:
        raise ValueError("必要な環境変数が設定されていません")

    client = storage.Client.from_service_account_json(credentials)
    bucket = storage.Bucket(client, bucket_name)

    for filename in files:
        if not uid or not uid.strip():
            raise ValueError("Invalid user ID")

        safe_uid = uid.strip().rstrip("/")
        normalized_blobname = unicodedata.normalize("NFC", f"{safe_uid}/{filename}")
        blob = bucket.blob(normalized_blobname)

        try:
            # ファイルの存在確認を追加
            exists = await asyncio.to_thread(blob.exists)
            if not exists:
                error_message = f"ファイル {normalized_blobname} が存在しません"
                failed_files.append(error_message)
                logging.warning(error_message)
                continue

            # メタデータを取得して詳細なログを残す
            blob_metadata = blob.metadata if blob.metadata else {}
            logging.info(f"削除開始: {normalized_blobname}, メタデータ: {blob_metadata}")

            await asyncio.to_thread(blob.delete)
            success_message = f"ファイル {normalized_blobname} が削除されました"
            success_files.append({"message": success_message, "filename": normalized_blobname})
            logging.info(success_message)

        except GoogleAPIError as e:
            error_message = (
                f"GCS API エラー - ファイル: {normalized_blobname}, "
                f"エラーコード: {getattr(e, 'code', 'unknown')}, "
                f"詳細: {str(e)}"
            )
            failed_files.append(error_message)
            logging.error(error_message)

        except Exception as e:
            error_message = (
                f"予期しないエラー - ファイル: {normalized_blobname}, "
                f"エラータイプ: {type(e).__name__}, "
                f"詳細: {str(e)}"
            )
            failed_files.append(error_message)
            logging.error(error_message, exc_info=True)  # スタックトレースも記録

    if failed_files:
        error_details = "\n".join(failed_files)
        return {
            "success": False,
            "success_files": success_files,
            "failed_files": error_details,
        }

    return {"success": True, "success_files": success_files}


async def generate_upload_signed_url_v4(files: list[str], uid: str) -> dict:
    """
    指定されたファイルリストに対して、Google Cloud Storageにアップロードするための
    署名付きURLを生成します。

    :param files: アップロードするファイル名のリスト
    :type files: list[str]
    :return: ファイル名をキーとし、署名付きURLを値とする辞書
    :rtype: dict
    """
    upload_signed_urls = {}

    # 環境変数から認証情報を取得
    credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    bucket_name = os.getenv("BUCKET_NAME")

    client = storage.Client.from_service_account_json(credentials)
    bucket = storage.Bucket(client, bucket_name)
    for file in files:
        # ブロブ名を正規化
        normalized_blobname = unicodedata.normalize("NFC", uid + "/" + file)
        blob = bucket.blob(normalized_blobname)

        url = await asyncio.to_thread(
            blob.generate_signed_url,
            version="v4",
            expiration=datetime.timedelta(minutes=15),
            method="PUT",
            content_type="application/octet-stream",
        )
        """
        デバッグ用の出力
        print("Generated PUT signed URL:")
        print(url)
        print("You can use this URL with any user agent, for example:")
        print(
            "curl -X PUT -H 'Content-Type: application/octet-stream' "
            "--upload-file my-file '{}'".format(url)
        )
        """
        upload_signed_urls[normalized_blobname] = url
    return upload_signed_urls


async def generate_download_signed_url_v4(files: list[str], uid: str) -> dict:
    download_signed_urls = {}

    # 環境変数から認証情報を取得
    credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    bucket_name = os.getenv("BUCKET_NAME")

    if not credentials or not bucket_name:
        raise ValueError("必要な環境変数が設定されていません")

    # ユーザーIDの検証
    if not uid or not uid.strip():
        raise ValueError("Invalid user ID")

    client = storage.Client.from_service_account_json(credentials)
    bucket = storage.Bucket(client, bucket_name)

    for filename in files:
        try:
            # パスの正規化
            safe_uid = uid.strip().rstrip("/")
            normalized_blobname = unicodedata.normalize("NFC", f"{safe_uid}/{filename}")
            blob = bucket.blob(normalized_blobname)

            # ファイルの存在確認
            exists = await asyncio.to_thread(blob.exists)
            if not exists:
                logging.warning(f"ファイル {normalized_blobname} が存在しません")
                continue

            # ファイルの拡張子に基づいてContent-Typeを設定
            if filename.lower().endswith(".pdf"):
                response_type = "application/pdf"
            elif filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                response_type = "image/*"
            elif filename.lower().endswith((".mp4", ".mov", ".avi")):
                response_type = "video/*"
            elif filename.lower().endswith((".mp3", ".wav")):
                response_type = "audio/*"
            else:
                response_type = "application/octet-stream"

            url = await asyncio.to_thread(
                blob.generate_signed_url,
                version="v4",
                expiration=datetime.timedelta(minutes=15),
                method="GET",
                response_disposition="inline",
                response_type=response_type,
            )

            download_signed_urls[normalized_blobname] = url

        except GoogleAPIError as e:
            error_message = (
                f"GCS API エラー - ファイル: {filename}, "
                f"エラーコード: {getattr(e, 'code', 'unknown')}, "
                f"詳細: {str(e)}"
            )
            logging.error(error_message)
            continue

        except Exception as e:
            error_message = (
                f"予期しないエラー - ファイル: {filename}, "
                f"エラータイプ: {type(e).__name__}, "
                f"詳細: {str(e)}"
            )
            logging.error(error_message, exc_info=True)
            continue

    return download_signed_urls
