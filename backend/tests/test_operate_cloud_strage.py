import os
import io
import pytest
from dotenv import load_dotenv
from fastapi import UploadFile, HTTPException
from fastapi.testclient import TestClient
from app.utils.operate_cloud_storage import post_files, upload_files
from app.main import app
from unittest.mock import patch
from google.api_core.exceptions import GoogleAPIError


load_dotenv()  # 環境変数の読み込み

client = TestClient(app)


@pytest.mark.asyncio
async def test_post_files_with_valid_extension() -> None:
    # アップロードするダミーファイル名
    file_paths = [
        "5_アジャイルⅡ.pdf",
        "AI-powered Code Review with LLM.pdf",
    ]

    # BytesIOでダミーファイルを作成してリクエストデータを作成
    files: list[UploadFile] = []
    for file_path in file_paths:
        dummy_content = b"dummy pdf content"  # ダミーのPDFコンテンツ (必要に応じて変更)
        files.append(UploadFile(file=io.BytesIO(dummy_content), filename=file_path))

    result = await post_files(files)

    # 結果の検証
    assert result["success"] == True
    assert len(result["success_files"]) == 2  # 成功したファイル数を検証


@pytest.mark.asyncio
async def test_upload_files_with_invalid_extension() -> None:
    # 無効な拡張子のファイル名
    invalid_file_names = ["test001.txt", "test002.txt"]

    # BytesIOでダミーファイルを作成してリクエストデータを作成
    invalid_files = []
    for file_name in invalid_file_names:
        dummy_content = b"dummy text content"  # ダミーのテキストコンテンツ
        invalid_files.append(
            UploadFile(file=io.BytesIO(dummy_content), filename=file_name)
        )

    # post_files関数を直接呼び出す
    with pytest.raises(HTTPException) as exc_info:
        await post_files(invalid_files)

    # 例外の内容を検証
    assert exc_info.value.status_code == 400
    assert "アップロード対象外の拡張子です。" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_upload_files() -> None:
    # アップロードするダミーファイル名
    file_paths = [
        "5_アジャイルⅡ.pdf",
        "AI-powered Code Review with LLM.pdf",
    ]

    # BytesIOでダミーファイルを作成してリクエストデータを作成
    files: list[UploadFile] = []
    for file_path in file_paths:
        dummy_content = b"dummy pdf content"  # ダミーのPDFコンテンツ (必要に応じて変更)
        files.append(UploadFile(file=io.BytesIO(dummy_content), filename=file_path))

    result = await post_files(files)

    # 結果の検証
    assert result["success"] == True
    assert len(result["success_files"]) == 2  # 成功したファイル数を検証


@pytest.mark.asyncio
async def test_upload_files_with_failure() -> None:
    # アップロードするダミーファイル名
    file_paths = [
        "5_アジャイルⅡ.pdf",
        "AI-powered Code Review with LLM.pdf",
    ]

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
        result = await upload_files(files)

        # 結果の検証
        assert result["success"] == False
        assert len(result["success_files"]) == 0  # 成功したファイル数は0
        assert (
            "Upload failed" in result["failed_files"]
        )  # 失敗したファイルのエラーメッセージを検証
