import io
import logging
import os

from dotenv import load_dotenv
from google.cloud import storage

# 環境変数を読み込む
load_dotenv()

# ログの設定
logging.basicConfig(level=logging.INFO)


# 環境変数から認証情報を取得
GOOGLE_APPLICATION_CREDENTIALS_JSON: str | None = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS_JSON"
)


# 認証情報が設定されていない場合はエラーを発生させる
if GOOGLE_APPLICATION_CREDENTIALS_JSON is None:
    raise ValueError("認証情報が設定されていません")
else:
    credentials = GOOGLE_APPLICATION_CREDENTIALS_JSON


# GCSにファイルをアップロードする関数
def upload_blob(
    bucket_name: str,
    source_file_name: str,
    destination_blob_name: str,
    credentials: str = credentials,
) -> None:
    """Uploads a file to the bucket."""
    client = storage.Client.from_service_account_json(credentials)

    # 作成したバケットの名前を指定します
    bucket = storage.Bucket(client, bucket_name)
    blob = bucket.blob(destination_blob_name)

    # ファイルをアップロード(同じファイル名は上書きされます)
    blob.upload_from_filename(source_file_name)

    # ログ出力
    logging.info(f"File {source_file_name} uploaded to {destination_blob_name}.")


# GCSにストリーミングでアップロードする関数
def upload_blob_from_stream(
    bucket_name: str,
    file_obj: io.BytesIO,
    destination_blob_name: str,
    credentials: str = credentials,
) -> None:
    """Uploads bytes from a stream or other file-like object to a blob."""

    file_obj = io.BytesIO()
    client = storage.Client.from_service_account_json(credentials)
    bucket = storage.Bucket(client, bucket_name)
    blob = bucket.blob(destination_blob_name)

    # オブジェクトを先頭に戻す
    file_obj.seek(0)

    # ストリームデータをアップロード
    blob.upload_from_file(file_obj)

    # ログ出力
    logging.info(
        f"Stream data uploaded to {destination_blob_name} in bucket {bucket_name}."
    )
