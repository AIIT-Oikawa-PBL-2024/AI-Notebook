from typing import AsyncGenerator

import pytest
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.main import app
from app.models.users import User

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


# ファイル削除のテスト
@pytest.mark.asyncio
async def test_delete_file(session: AsyncSession) -> None:
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

        response = await client.delete("/files/1")
        print(response.text)  # デバッグ用出力
        assert response.status_code == 200
        data = response.json()
        assert data["detail"] == "ファイルが削除されました"


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


# 存在しないファイルIDによるファイル削除のテスト
@pytest.mark.asyncio
async def test_delete_file_not_found(session: AsyncSession) -> None:
    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        response = await client.delete("/files/9999")
        print(response.text)  # デバッグ用出力
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "ファイルが見つかりません"
