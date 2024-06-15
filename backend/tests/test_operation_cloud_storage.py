import os
import io
import pytest
from dotenv import load_dotenv
from fastapi import UploadFile, HTTPException
from fastapi.testclient import TestClient
from app.utils.operation_cloud_storage import post_files, upload_files
from app.main import app 
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from google.cloud import exceptions as google_exceptions
from unittest.mock import patch

load_dotenv()  # 環境変数の読み込み

client = TestClient(app)

@pytest.mark.asyncio
async def test_post_files_with_valid_extension():
    # アップロードするファイルのパス
    file_paths = ["tests/5_アジャイルⅡ.pdf", "tests/AI-powered Code Review with LLM.pdf"]

    # ファイルを開いてリクエストデータを作成
    files = []
    for file_path in file_paths:
        with open(file_path, "rb") as file:
            file_content = file.read()
            file_content = file.read()
            file_name = os.path.basename(file_path)
            files.append(UploadFile(file=io.BytesIO(file_content), filename=file_name))

    # post＿files関数を直接呼び出す
    result = await post_files(files)

    # 結果の検証
    assert result["success"] == True
    assert len(result["success_files"]) == 2  # 成功したファイル数を検証

@pytest.mark.asyncio
async def test_upload_files_with_invalid_extension():
    # 無効な拡張子のファイルのパス
    invalid_file_paths = ["tests/test001.txt", "tests/test002.txt"]

    # 無効な拡張子のファイルを開いてリクエストデータを作成
    invalid_files = []
    for file_path in invalid_file_paths:
        with open(file_path, "rb") as file:
            file_content = file.read()
            file_name = os.path.basename(file_path)
            invalid_files.append(UploadFile(file=io.BytesIO(file_content), filename=file_name))

    # post_files関数を直接呼び出す
    with pytest.raises(HTTPException) as exc_info:
        await post_files(invalid_files)

    # 例外の内容を検証
    assert exc_info.value.status_code == 400
    assert "拡張子がアップロード対象外のファイルです" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_upload_files():
    # アップロードするファイルのパス
    file_paths = ["tests/5_アジャイルⅡ.pdf", "tests/AI-powered Code Review with LLM.pdf"]

    # ファイルを開いてUploadFileオブジェクトを作成
    files = []
    for file_path in file_paths:
        with open(file_path, "rb") as file:
            file_content = file.read()
            file_name = os.path.basename(file_path)
            files.append(UploadFile(file=io.BytesIO(file_content), filename=file_name))

    # upload_files関数を直接呼び出す
    result = await upload_files(files)

    # 結果の検証
    assert result["success"] == True
    assert len(result["success_files"]) == 2  # 成功したファイル数を検証

@pytest.mark.asyncio
async def test_upload_files_with_failure():
    # アップロードするファイルのパス
    file_paths = ["tests/5_アジャイルⅡ.pdf", "tests/AI-powered Code Review with LLM.pdf"]

    # ファイルを開いてUploadFileオブジェクトを作成
    files = []
    for file_path in file_paths:
        with open(file_path, "rb") as file:
            file_content = file.read()
            file_name = os.path.basename(file_path)
            files.append(UploadFile(file=io.BytesIO(file_content), filename=file_name))

    # upload_files関数内で発生する例外をモックする
    with patch("google.cloud.storage.Blob.upload_from_file", side_effect=google_exceptions.GoogleCloudError("Upload failed")):
        # upload_files関数を直接呼び出す
        result = await upload_files(files)

        # 結果の検証
        assert result["success"] == False
        assert len(result["success_files"]) == 0  # 成功したファイル数は0
        assert "Upload failed" in result["failed_files"]  # 失敗したファイルのエラーメッセージを検証
