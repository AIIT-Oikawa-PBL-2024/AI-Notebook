import os
import io
import pytest
from dotenv import load_dotenv
from fastapi import UploadFile
from fastapi.testclient import TestClient
from app.utils.operation_cloud_storage import post_files
from app.main import app  # FastAPIアプリケーションのインスタンス

load_dotenv()  # 環境変数の読み込み

client = TestClient(app)

def test_upload_files():
    # アップロードするファイルのパス
    file_paths = ["tests/5_アジャイルⅡ.pdf", "tests/AI-powered Code Review with LLM.pdf"]

    # ファイルを開いてリクエストデータを作成
    files = []
    for file_path in file_paths:
        with open(file_path, "rb") as file:
            file_content = file.read()
            file_name = os.path.basename(file_path)
            file_obj = io.BytesIO(file_content)
            files.append(("files", (file_name, file_obj)))

    # ファイルアップロードのリクエストを送信
    response = client.post("/files/upload", files=files)

    # レスポンスのステータスコードの検証
    assert response.status_code == 200

    # レスポンスの内容の検証
    assert response.json() == {"success": True}

def test_upload_files_with_invalid_extension():
    # 無効な拡張子のファイルのパス
    invalid_file_paths = ["tests/test001.txt", "tests/test002.txt"]

    # 無効な拡張子のファイルを開いてリクエストデータを作成
    invalid_files = []
    for file_path in invalid_file_paths:
        with open(file_path, "rb") as file:
            file_content = file.read()
            file_name = os.path.basename(file_path)
            file_obj = io.BytesIO(file_content)
            invalid_files.append(("files", (file_name, file_obj)))

    # ファイルアップロードのリクエストを送信
    response = client.post("/files/upload", files=invalid_files)

    # レスポンスのステータスコードの検証
    assert response.status_code == 400

    # レスポンスの内容の検証
    assert "拡張子がアップロード対象外のファイルです" in response.json()["detail"]
