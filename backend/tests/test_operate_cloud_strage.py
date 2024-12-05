import os
import io
import pytest
from dotenv import load_dotenv
from fastapi import UploadFile, HTTPException
from fastapi.testclient import TestClient
from app.utils.operate_cloud_storage import (
    post_files,
    upload_files,
    delete_files_from_gcs,
    generate_upload_signed_url_v4,
    generate_download_signed_url_v4,
)
from app.main import app
from unittest.mock import patch, MagicMock, Mock, call
from google.api_core.exceptions import GoogleAPIError, NotFound
import unicodedata
from google.cloud import storage

load_dotenv()  # 環境変数の読み込み

client = TestClient(app)


@pytest.mark.asyncio
async def test_post_files_with_valid_extension() -> None:
    """
    有効な拡張子を持つファイルのアップロードをテストする関数

    :param None: この関数にはパラメータがありません。
    :return: None
    :raises AssertionError: テストが失敗した場合
    """
    # アップロードするダミーファイル名
    file_paths = [
        "5_アジャイルⅡ.pdf",
        "AI-powered Code Review with LLM.pdf",
    ]

    # ユーザーID
    uid = "test_user"

    # BytesIOでダミーファイルを作成してリクエストデータを作成
    files: list[UploadFile] = []
    for file_path in file_paths:
        dummy_content = b"dummy pdf content"  # ダミーのPDFコンテンツ (必要に応じて変更)
        files.append(UploadFile(file=io.BytesIO(dummy_content), filename=file_path))

    result = await post_files(files, uid)

    # 結果の検証
    assert result["success"] == True
    assert len(result["success_files"]) == 2  # 成功したファイル数を検証


@pytest.mark.asyncio
async def test_upload_files_with_invalid_extension() -> None:
    """
    無効な拡張子を持つファイルのアップロード時のエラー処理をテストする関数

    :param None: この関数にはパラメータがありません。
    :return: None
    :raises AssertionError: テストが失敗した場合
    """
    # 無効な拡張子のファイル名
    invalid_file_names = ["test001.txt", "test002.txt"]

    # ユーザーID
    uid = "test_user"

    # BytesIOでダミーファイルを作成してリクエストデータを作成
    invalid_files = []
    for file_name in invalid_file_names:
        dummy_content = b"dummy text content"  # ダミーのテキストコンテンツ
        invalid_files.append(UploadFile(file=io.BytesIO(dummy_content), filename=file_name))

    # post_files関数を直接呼び出す
    with pytest.raises(HTTPException) as exc_info:
        await post_files(invalid_files, uid)

    # 例外の内容を検証
    assert exc_info.value.status_code == 400
    assert "アップロード対象外の拡張子です。" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_upload_files() -> None:
    """
    ファイルのアップロード機能をテストする関数

    :param None: この関数にはパラメータがありません。
    :return: None
    :raises AssertionError: テストが失敗した場合
    """
    # アップロードするダミーファイル名
    file_paths = [
        "5_アジャイルⅡ.pdf",
        "AI-powered Code Review with LLM.pdf",
    ]

    # ユーザーID
    uid = "test_user"

    # BytesIOでダミーファイルを作成してリクエストデータを作成
    files: list[UploadFile] = []
    for file_path in file_paths:
        dummy_content = b"dummy pdf content"  # ダミーのPDFコンテンツ (必要に応じて変更)
        files.append(UploadFile(file=io.BytesIO(dummy_content), filename=file_path))

    result = await post_files(files, uid)

    # 結果の検証
    assert result["success"] == True
    assert len(result["success_files"]) == 2  # 成功したファイル数を検証


@pytest.mark.asyncio
async def test_upload_files_with_failure() -> None:
    """
    ファイルアップロード失敗時のエラー処理をテストする関数

    :param None: この関数にはパラメータがありません。
    :return: None
    :raises AssertionError: テストが失敗した場合
    """
    # アップロードするダミーファイル名
    file_paths = [
        "5_アジャイルⅡ.pdf",
        "AI-powered Code Review with LLM.pdf",
    ]

    # ユーザーID
    uid = "test_user"

    # BytesIOでダミーファイルを作成してリクエストデータを作成
    files: list[UploadFile] = []
    for file_path in file_paths:
        dummy_content = b"dummy pdf content"  # ダミーのPDFコンテンツ (必要に応じて変更)
        files.append(UploadFile(file=io.BytesIO(dummy_content), filename=file_path))

    # upload_files関数内で発生する例外をモックする
    with patch(
        "google.cloud.storage.Blob.upload_from_file",
        side_effect=GoogleAPIError("Upload failed"),
    ):
        # upload_files関数を直接呼び出す
        result = await upload_files(files, uid)

        # 結果の検証
        assert result["success"] == False
        assert len(result["success_files"]) == 0  # 成功したファイル数は0
        assert "Upload failed" in result["failed_files"]  # 失敗したファイルのエラーメッセージを検証


# NFD形式の日本語ファイル名のブロブ名がNFC形式に正規化されていることを確認するテスト
@pytest.mark.asyncio
async def test_upload_files_nfc_normalization() -> None:
    """
    日本語ファイル名のNFC正規化をテストする関数

    :param None: この関数にはパラメータがありません。
    :return: None
    :raises AssertionError: テストが失敗した場合
    """

    # ユーザーID
    uid = "test_user"

    # NFD形式（濁点が分離された形式）の日本語ファイル名
    nfd_filename = "テスト" + "\u3099" + "ファイル.pdf"  # "テストゞファイル.pdf"のNFD形式
    nfc_filename = unicodedata.normalize("NFC", nfd_filename)

    # BytesIOでダミーファイルを作成
    dummy_content = b"dummy pdf content"
    file = UploadFile(file=io.BytesIO(dummy_content), filename=nfd_filename)

    # Google Cloud Storageのモックを作成
    mock_blob = MagicMock()
    mock_bucket = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    mock_client = MagicMock()
    mock_client.bucket.return_value = mock_bucket

    # パッチを適用してGoogle Cloud Storageの操作をモック
    with (
        patch(
            "google.cloud.storage.Client.from_service_account_json",
            return_value=mock_client,
        ),
        patch("google.cloud.storage.Bucket", return_value=mock_bucket),
        patch("os.getenv", return_value="mock_value"),
    ):
        # upload_files関数を呼び出す
        result = await upload_files([file], uid)

        # アサーション
        assert result["success"] is True
        assert len(result["success_files"]) == 1

        # bucket.blob()が正規化されたファイル名で呼び出されたことを確認
        mock_bucket.blob.assert_called_once()
        called_filename = mock_bucket.blob.call_args[0][0]
        assert called_filename == "test_user/" + nfc_filename
        assert called_filename != "test_user/" + nfd_filename
        assert unicodedata.is_normalized("NFC", called_filename)


@pytest.mark.asyncio
async def test_delete_files_from_gcs() -> None:
    """
    Google Cloud Storageからのファイル削除機能をテストする関数

    :param None: この関数にはパラメータがありません。
    :return: None
    :raises AssertionError: テストが失敗した場合
    """
    # アップロードするダミーファイル名
    file_paths = [
        "5_アジャイルⅡ.pdf",
        "AI-powered Code Review with LLM.pdf",
    ]

    # ユーザーID
    uid = "test_user"

    # 通常の削除テスト
    # BytesIOでダミーファイルを作成してリクエストデータを作成
    files: list[UploadFile] = []
    for file_path in file_paths:
        dummy_content = b"dummy pdf content"  # ダミーのPDFコンテンツ
        files.append(UploadFile(file=io.BytesIO(dummy_content), filename=file_path))

    # ファイルをアップロード
    await post_files(files, uid)

    # 削除するファイル名のリスト
    deletefiles: list[str] = [
        "5_アジャイルⅡ.pdf",
        "AI-powered Code Review with LLM.pdf",
    ]

    # 正常系: ファイルの削除
    result = await delete_files_from_gcs(deletefiles, uid)

    # 結果の検証
    assert result["success"] == True
    assert len(result["success_files"]) == 2  # 削除に成功したファイル数を検証

    # 異常系: Google API エラーのテスト
    error_message = "Delete failed"
    with patch(
        "google.cloud.storage.Bucket.blob",
        return_value=MagicMock(
            exists=MagicMock(return_value=True),
            delete=MagicMock(side_effect=GoogleAPIError(error_message)),
        ),
    ):
        result = await delete_files_from_gcs(deletefiles, uid)
        assert result["success"] == False
        expected_error = f"GCS API エラー - ファイル: test_user/5_アジャイルⅡ.pdf, エラーコード: unknown, 詳細: {error_message}"
        assert expected_error in result["failed_files"]

    # 異常系: ファイルが存在しない場合のテスト
    with patch(
        "google.cloud.storage.Bucket.blob",
        return_value=MagicMock(exists=MagicMock(return_value=False)),
    ):
        result = await delete_files_from_gcs(deletefiles, uid)
        assert result["success"] == False
        expected_error = "ファイル test_user/5_アジャイルⅡ.pdf が存在しません"
        assert expected_error in result["failed_files"]


@pytest.mark.asyncio
async def test_generate_upload_signed_url_v4() -> None:
    # 署名付きURLを作成するファイル名のリスト
    testfiles: list[str] = [
        "5_アジャイルⅡ.pdf",
        "AI-powered Code Review with LLM.pdf",
    ]

    # ユーザーID
    uid = "test_user"

    # 署名付きURLを作成する
    result = await generate_upload_signed_url_v4(testfiles, uid)

    # 結果の検証
    assert result["test_user/5_アジャイルⅡ.pdf"] is not None
    assert result["test_user/AI-powered Code Review with LLM.pdf"] is not None
    assert len(result) == 2


@pytest.mark.asyncio
async def test_generate_download_signed_url_v4() -> None:
    """generate_download_signed_url_v4 の基本機能テスト"""
    # テスト用のファイルリスト
    test_files = [
        "5_アジャイルⅡ.pdf",
        "AI-powered Code Review with LLM.pdf",
    ]
    uid = "test_user"

    # 環境変数の設定
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "dummy_credentials.json"
    os.environ["BUCKET_NAME"] = "test-bucket"

    # GCSのモックを設定
    with (
        patch("google.cloud.storage.Client") as mock_client,
        patch("google.cloud.storage.Bucket") as mock_bucket,
    ):
        # blobのモックを設定
        mock_blob = Mock()
        mock_blob.exists.return_value = True
        mock_blob.generate_signed_url.return_value = "https://example.com/signed-url"
        mock_bucket.return_value.blob.return_value = mock_blob

        # テスト実行
        result: dict[str, str] = await generate_download_signed_url_v4(test_files, uid)

        # 結果の検証
        assert len(result) == 2
        assert f"{uid}/5_アジャイルⅡ.pdf" in result
        assert f"{uid}/AI-powered Code Review with LLM.pdf" in result
        assert all(isinstance(url, str) for url in result.values())
        assert all(url.startswith("https://") for url in result.values())


@pytest.mark.asyncio
async def test_generate_download_signed_url_v4_with_invalid_inputs() -> None:
    """無効な入力パラメータのテスト"""
    # 環境変数の設定
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "dummy_credentials.json"
    os.environ["BUCKET_NAME"] = "test-bucket"

    # 空のユーザーIDでテスト
    with pytest.raises(ValueError, match="Invalid user ID"):
        await generate_download_signed_url_v4(["test.pdf"], "")

    with pytest.raises(ValueError, match="Invalid user ID"):
        await generate_download_signed_url_v4(["test.pdf"], "   ")


@pytest.mark.asyncio
async def test_generate_download_signed_url_v4_with_missing_env_vars() -> None:
    """環境変数が設定されていない場合のテスト"""
    # 環境変数をクリア
    os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
    os.environ.pop("BUCKET_NAME", None)

    with pytest.raises(ValueError, match="必要な環境変数が設定されていません"):
        await generate_download_signed_url_v4(["test.pdf"], "test_user")


@pytest.mark.asyncio
async def test_generate_download_signed_url_v4_with_gcs_error() -> None:
    """GCS APIエラーが発生した場合のテスト"""
    test_files = ["error.pdf"]
    uid = "test_user"

    # 環境変数の設定
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "dummy_credentials.json"
    os.environ["BUCKET_NAME"] = "test-bucket"

    with (
        patch("google.cloud.storage.Client") as mock_client,
        patch("google.cloud.storage.Bucket") as mock_bucket,
    ):
        # GCS APIエラーをシミュレート
        mock_blob = Mock()
        mock_blob.exists.return_value = True
        mock_blob.generate_signed_url.side_effect = NotFound("File not found")
        mock_bucket.return_value.blob.return_value = mock_blob

        # テスト実行
        result = await generate_download_signed_url_v4(test_files, uid)

        # エラーが処理され、空の結果が返されることを確認
        assert len(result) == 0
