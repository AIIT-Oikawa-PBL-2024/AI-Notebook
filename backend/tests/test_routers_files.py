from distutils import filelist
from typing import AsyncGenerator

import pytest
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.main import app
from app.models.users import User
import unicodedata

# .envファイルから環境変数を読み込む
load_dotenv()


# sessionフィクスチャを提供するフィクスチャを定義
@pytest.fixture
async def session(
    setup_and_teardown_database: AsyncGenerator[AsyncSession, None],
) -> AsyncGenerator[AsyncSession, None]:
    async with setup_and_teardown_database as session:  # type: ignore
        yield session
    await session.close()


# ユーザーIDを取得するためのヘルパー関数
async def get_user_id(session: AsyncSession) -> int:
    result = await session.execute(select(User).where(User.email == "test@example.com"))
    user = result.scalar()
    if user is None:
        raise ValueError("Test user not found")
    return int(user.id)


# ファイルアップロードのテスト
@pytest.mark.asyncio
async def test_upload_files(session: AsyncSession) -> None:
    user_id = await get_user_id(session)

    file_content = b"test file content"
    files = [
        ("files", ("test_file.pdf", file_content, "application/pdf")),
    ]
    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        response = await client.post(f"/files/upload?user_id={user_id}", files=files)
        print(response.text)  # デバッグ用出力
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["success_files"]) == 1


# ファイル一覧取得のテスト
@pytest.mark.asyncio
async def test_get_files(session: AsyncSession) -> None:
    user_id = await get_user_id(session)

    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        file_content = b"test file content"
        files = [
            ("files", ("test_file.pdf", file_content, "application/pdf")),
        ]
        await client.post(f"/files/upload?user_id={user_id}", files=files)

        response = await client.get("/files/")
        print(response.text)  # デバッグ用出力
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0


# ファイルIDによるファイル取得のテスト
@pytest.mark.asyncio
async def test_get_file_by_id(session: AsyncSession) -> None:
    user_id = await get_user_id(session)

    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        file_content = b"test file content"
        files = [
            ("files", ("test_file.pdf", file_content, "application/pdf")),
        ]
        await client.post(f"/files/upload?user_id={user_id}", files=files)

        response = await client.get("/files/1")
        print(response.text)  # デバッグ用出力
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["file_name"] == "test_file.pdf"


# ファイル名のリストとユーザーIDによるファイルの削除のテスト
@pytest.mark.asyncio
async def test_delete_files(session: AsyncSession) -> None:
    user_id = await get_user_id(session)

    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        file_content = b"test file content"
        files = [
            ("files", ("test_file1.pdf", file_content, "application/pdf")),
            ("files", ("test_file2.pdf", file_content, "application/pdf")),
        ]
        await client.post(f"/files/upload?user_id={user_id}", files=files)

        delete_files = ["test_file1.pdf", "test_file2.pdf"]
        response = await client.request(
            method="DELETE",
            url=f"/files/delete_files?user_id={user_id}",
            json=delete_files,
        )
        print(response.text)  # デバッグ用出力
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["success_files"]) == 2
        assert len(data["failed_files"]) == 0


# 存在しないファイルIDによるファイル取得のテスト
@pytest.mark.asyncio
async def test_get_file_by_id_not_found(session: AsyncSession) -> None:
    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        response = await client.get("/files/9999")
        print(response.text)  # デバッグ用出力
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "ファイルが見つかりません"


# 濁点を含むファイル名のNFC正規化テスト
@pytest.mark.asyncio
async def test_upload_file_with_dakuten(session: AsyncSession) -> None:
    user_id = await get_user_id(session)

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
        response = await client.post(f"/files/upload?user_id={user_id}", files=files)
        print(response.text)  # デバッグ用出力
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["success_files"]) == 1

        # アップロードされたファイルの情報を取得
        file_response = await client.get("/files/")
        assert file_response.status_code == 200
        file_data = file_response.json()

        # 最後にアップロードされたファイルのファイル名を確認
        uploaded_filename = file_data[-1]["file_name"]

        # ファイル名がNFC形式になっていることを確認
        assert uploaded_filename == nfc_filename
        assert uploaded_filename != nfd_filename
        assert unicodedata.is_normalized("NFC", uploaded_filename)
