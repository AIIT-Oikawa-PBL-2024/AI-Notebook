from typing import Generator
from unittest import mock

import pytest
from google.resumable_media.requests.upload import MultipartUpload

from app.utils.operation_cloud_storage import upload_blob


# GCSクライエントのモックを作成
@pytest.fixture
def mock_storage_client() -> Generator[mock.Mock, None, None]:
    with mock.patch("google.cloud.storage.Client") as MockClient:
        yield MockClient


# GCSバケットのモックを作成
@pytest.fixture
def mock_bucket(mock_storage_client: mock.Mock) -> Generator[mock.Mock, None, None]:
    mock_bucket = mock_storage_client().bucket()
    yield mock_bucket


# アップロード処理のテスト
def test_upload_blob(mock_bucket: mock.Mock) -> None:
    # テストの準備
    bucket_name = "test_bucket"
    source_file_name = "test_file.pdf"
    destination_blob_name = "test_file.pdf"
    credentials = "mock_credentials.json"
    file_content = b"data" * 6

    # モックの設定
    mock_blob = mock_bucket.blob(destination_blob_name)
    mock_blob.upload_from_filename.return_value = None

    # HTTPリクエストのモックレスポンスを設定
    with mock.patch.object(
        MultipartUpload,
        "_prepare_request",
        return_value=(
            "POST",
            "http://mock.url",
            file_content,
            {"Content-Type": "application/pdf"},
        ),
    ):
        with mock.patch.object(
            MultipartUpload,
            "_process_response",
            return_value=mock.Mock(status_code=200),
        ):
            with mock.patch(
                "builtins.open", mock.mock_open(read_data=file_content)
            ) as mock_file:
                # テスト実行
                print("Before upload_blob call")
                upload_blob(
                    bucket_name, source_file_name, destination_blob_name, credentials
                )
                print("After upload_blob call")
                # ファイルを開くことを確認
                mock_file.assert_any_call(source_file_name, "rb")
