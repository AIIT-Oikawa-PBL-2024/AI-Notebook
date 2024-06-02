import os
import pytest
from dotenv import load_dotenv
from fastapi import UploadFile
from fastapi.testclient import TestClient
from app.cruds import files as files_crud
from app.main import app  # FastAPIアプリケーションのインスタンス

load_dotenv()  # 環境変数の読み込み

client = TestClient(app)

def test_post_files_success():
    # テストに使用するファイルのパス
    file_paths = ["tests/5_アジャイルⅡ.pdf", "tests/AI-powered Code Review with LLM.pdf"]
    
    # UploadFileオブジェクトの作成
    upload_files = [
        UploadFile(filename=os.path.basename(path), file=open(path, "rb"))
        for path in file_paths
        ]  
    # リクエストの送信
    response = client.post("/files/", files=[("files", file) for file in upload_files])
    
    # レスポンスのステータスコードの検証
    assert response.status_code == 200
    
    # レスポンスの内容の検証
    response_data = response.json()
    assert "success" in response_data
    assert response_data["success"] == True
    assert "success_files" in response_data
    assert len(response_data["success_files"]) == len(file_paths)

def test_post_files_invalid_extension():
    # 無効な拡張子のファイルのパス
    file_paths = ["tests/test001.txt", "tests/test002.txt"]
    
    # UploadFileオブジェクトの作成
    upload_files = [
        UploadFile(filename=os.path.basename(path), file=open(path, "rb"))
        for path in file_paths
        ]
        
    # リクエストの送信
    response = client.post("/files/", files=[("files", file) for file in upload_files])
    
    # レスポンスのステータスコードの検証
    assert response.status_code == 400
    
    # レスポンスの内容の検証
    response_data = response.json()
    assert "detail" in response_data
    assert "拡張子がアップロード対象外のファイルです" in response_data["detail"]

@pytest.mark.asyncio
async def test_upload_files_success():
    # テストに使用するファイルのパス
    file_paths = ["tests/5_アジャイルⅡ.pdf", "tests/AI-powered Code Review with LLM.pdf"]
    
    # UploadFileオブジェクトの作成
    upload_files = [
        UploadFile(filename=os.path.basename(path), file=open(path, "rb"))
        for path in file_paths
        ]    
    # upload_files関数の呼び出し
    result = await files_crud.upload_files(upload_files)
    
    # 結果の検証
    assert "success" in result
    assert result["success"] == True
    assert "success_files" in result
    assert len(result["success_files"]) == len(file_paths)