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
)
from app.main import app
from unittest.mock import patch, MagicMock
from google.api_core.exceptions import GoogleAPIError
import unicodedata


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
        invalid_files.append(
            UploadFile(file=io.BytesIO(dummy_content), filename=file_name)
        )

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
        assert (
            "Upload failed" in result["failed_files"]
        )  # 失敗したファイルのエラーメッセージを検証


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
    nfd_filename = (
        "テスト" + "\u3099" + "ファイル.pdf"
    )  # "テストゞファイル.pdf"のNFD形式
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

    # BytesIOでダミーファイルを作成してリクエストデータを作成
    files: list[UploadFile] = []
    for file_path in file_paths:
        dummy_content = b"dummy pdf content"  # ダミーのPDFコンテンツ (必要に応じて変更)
        files.append(UploadFile(file=io.BytesIO(dummy_content), filename=file_path))

    # ファイルをアップロード
    await post_files(files, uid)

    # 削除するファイル名のリスト
    deletefiles: list[str] = [
        "5_アジャイルⅡ.pdf",
        "AI-powered Code Review with LLM.pdf",
    ]

    # ファイルの削除
    result = await delete_files_from_gcs(deletefiles, uid)

    # 結果の検証
    assert result["success"] == True
    assert len(result["success_files"]) == 2  # 削除に成功したファイル数を検証

    # エラーハンドリングのテストケースを追加
    with patch(
        "google.cloud.storage.Blob.delete",
        side_effect=GoogleAPIError("Delete failed"),
    ):
        result = await delete_files_from_gcs(deletefiles, uid)
        assert result["success"] == False
        assert "Delete failed" in result["failed_files"]


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
