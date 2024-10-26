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
        raise HTTPException(
            status_code=500, detail="ファイルのアップロードに失敗しました"
        )

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
            normalized_blobname = unicodedata.normalize(
                "NFC", f"{safe_uid}/{file.filename}"
            )

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


async def delete_files_from_gcs(files: list[str], uid: str) -> dict:
    """
    Google Cloud Storageからファイルを削除します。

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
        # ユーザーIDの検証
        if not uid or not uid.strip():
            raise ValueError("Invalid user ID")

        # パスの正規化
        safe_uid = uid.strip().rstrip("/")
        normalized_blobname = unicodedata.normalize("NFC", f"{safe_uid}/{filename}")
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

        url = blob.generate_signed_url(
            version="v4",
            # This URL is valid for 15 minutes
            expiration=datetime.timedelta(minutes=15),
            # Allow PUT requests using this URL.
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
