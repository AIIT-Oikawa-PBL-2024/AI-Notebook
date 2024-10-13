from distutils import filelist
from typing import AsyncGenerator, Generator
import pytest
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
import unicodedata
import os
from unittest.mock import Mock
import jwt
import time
import os
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials


# .envファイルから環境変数を読み込む
load_dotenv()

# # テスト環境であることを示す環境変数を設定
# os.environ["TESTING"] = "True"


# # sessionフィクスチャを提供するフィクスチャを定義
# @pytest.fixture
# async def session(
#     setup_and_teardown_database: AsyncGenerator[AsyncSession, None],
# ) -> AsyncGenerator[AsyncSession, None]:
#     async with setup_and_teardown_database as session:  # type: ignore
#         yield session
#     await session.close()


# # テスト用のJWTトークンを生成する関数
# def generate_test_token(uid: str = "test_user") -> str:
#     payload = {
#         "uid": uid,
#         "exp": int(time.time()) + 3600,  # 1時間有効
#         "iat": int(time.time()),
#     }
#     secret = "test_secret"  # テスト用の秘密鍵
#     return jwt.encode(payload, secret, algorithm="HS256")


# # 認証をモックする関数
# def mock_authenticate_request(
#     request: Request, credentials: HTTPAuthorizationCredentials
# ) -> None:
#     request.state.uid = "test_user"
#     return None


# # テスト用のクライアントを作成
# test_token = generate_test_token()
# client = TestClient(app)
# client.headers.update({"Authorization": f"Bearer {test_token}"})

# # テスト用のダミーFirebase認証情報
# dummy_firebase_credentials = {
#     "type": "service_account",
#     "project_id": "dummy-project",
#     "private_key_id": "dummy-key-id",
#     "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC9hxWe/UJH1QAF\n-----END PRIVATE KEY-----\n",
#     "client_email": "dummy@dummy-project.iam.gserviceaccount.com",
#     "client_id": "123456789",
#     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#     "token_uri": "https://oauth2.googleapis.com/token",
#     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#     "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/dummy%40dummy-project.iam.gserviceaccount.com",
# }


# # 環境変数をモック
# @pytest.fixture(autouse=True)
# def mock_env_vars() -> Generator:
#     with patch.dict(
#         os.environ, {"FIREBASE_CREDENTIALS": str(dummy_firebase_credentials)}
#     ):
#         yield


# # 認証をモックするフィクスチャ
# @pytest.fixture(autouse=True)
# def mock_auth() -> Generator:
#     with patch("app.utils.user_auth.authenticate_request", mock_authenticate_request):
#         yield


# ファイルアップロードのテスト
@pytest.mark.asyncio
async def test_upload_files(session: AsyncSession, mock_auth: Mock) -> None:
    file_content = b"test file content"
    files = [
        ("files", ("test_file.pdf", file_content, "application/pdf")),
    ]
    headers = {"Authorization": "Bearer fake_token"}
    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        response = await client.post("/files/upload", files=files, headers=headers)
        print(response.text)  # デバッグ用出力
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["success_files"]) == 1


# ファイル一覧取得のテスト
@pytest.mark.asyncio
async def test_get_files(session: AsyncSession, mock_auth: Mock) -> None:
    headers = {"Authorization": "Bearer fake_token"}
    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        file_content = b"test file content"
        files = [
            ("files", ("test_file.pdf", file_content, "application/pdf")),
        ]
        await client.post(f"/files/upload", files=files, headers=headers)

        response = await client.get("/files/", headers=headers)
        print(response.text)  # デバッグ用出力
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0


# ファイルIDによるファイル取得のテスト
@pytest.mark.asyncio
async def test_get_file_by_id(session: AsyncSession, mock_auth: Mock) -> None:
    headers = {"Authorization": "Bearer fake_token"}
    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        file_content = b"test file content"
        files = [
            ("files", ("test_file.pdf", file_content, "application/pdf")),
        ]
        await client.post(f"/files/upload", files=files, headers=headers)

        response = await client.get("/files/1", headers=headers)
        print(response.text)  # デバッグ用出力
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["file_name"] == "test_file.pdf"


# ファイル名のリストとユーザーIDによるファイルの削除のテスト
@pytest.mark.asyncio
async def test_delete_files(session: AsyncSession, mock_auth: Mock) -> None:
    headers = {"Authorization": "Bearer fake_token"}
    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        file_content = b"test file content"
        files = [
            ("files", ("test_file1.pdf", file_content, "application/pdf")),
            ("files", ("test_file2.pdf", file_content, "application/pdf")),
        ]
        await client.post(f"/files/upload", files=files, headers=headers)

        delete_files = ["test_file1.pdf", "test_file2.pdf"]
        response = await client.request(
            method="DELETE",
            url="/files/delete_files",
            json=delete_files,
            headers=headers,
        )
        print(response.text)  # デバッグ用出力
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["success_files"]) == 2
        assert len(data["failed_files"]) == 0


# 存在しないファイルIDによるファイル取得のテスト
@pytest.mark.asyncio
async def test_get_file_by_id_not_found(session: AsyncSession, mock_auth: Mock) -> None:
    headers = {"Authorization": "Bearer fake_token"}
    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        response = await client.get("/files/9999", headers=headers)
        print(response.text)  # デバッグ用出力
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "ファイルが見つかりません"


# 濁点を含むファイル名のNFC正規化テスト
@pytest.mark.asyncio
async def test_upload_file_with_dakuten(session: AsyncSession, mock_auth: Mock) -> None:
    headers = {"Authorization": "Bearer fake_token"}

    # NFD形式（濁点が分離された形式）の日本語ファイル名
    nfd_filename = (
        "テスト" + "\u3099" + "ファイル.pdf"
    )  # "テストゞファイル.pdf"のNFD形式
    nfc_filename = unicodedata.normalize("NFC", nfd_filename)

    file_content = b"test file content with dakuten"
    files = [
        ("files", (nfd_filename, file_content, "application/pdf")),
    ]

    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        response = await client.post("/files/upload", files=files, headers=headers)
        print(response.text)  # デバッグ用出力
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["success_files"]) == 1

        # アップロードされたファイルの情報を取得
        file_response = await client.get("/files/", headers=headers)
        assert file_response.status_code == 200
        file_data = file_response.json()

        # 最後にアップロードされたファイルのファイル名を確認
        uploaded_filename = file_data[-1]["file_name"]

        # ファイル名がNFC形式になっていることを確認
        assert uploaded_filename == nfc_filename
        assert uploaded_filename != nfd_filename
        assert unicodedata.is_normalized("NFC", uploaded_filename)
