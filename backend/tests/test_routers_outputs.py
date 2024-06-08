from typing import AsyncGenerator

import pytest
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.main import app
from app.models.users import User

# .envから環境変数を読み込む
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


# 学習帳アップロードのテスト
@pytest.mark.asyncio
async def test_upload_outputs(session: AsyncSession) -> None:
    user_id = await get_user_id(session)

    outputs = {
        "output": "テストマークダウン絵文字",
        "user_id": user_id,
        "created_at": "2024-06-08T06:38:33.149Z",
        "id": 0
    }

    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        response = await client.post(f"/outputs/upload?user_id={user_id}", json=outputs)
        print(response.text)  # デバッグ用出力
        assert response.status_code == 200
        data = response.json()
        print(data)  # デバッグ用出力
        assert len(data) == 4
        assert data["output"] == "テストマークダウン絵文字"


# 学習帳一覧取得のテスト
@pytest.mark.asyncio
async def test_get_outputs(session: AsyncSession) -> None:
    user_id = await get_user_id(session)

    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        outputs = {
            "output": "テストマークダウン絵文字",
            "user_id": user_id,
            "created_at": "2024-06-08T06:38:33.149Z",
            "id": 0
        }
        await client.post(f"/outputs/upload?user_id={user_id}", json=outputs)

        response = await client.get("/outputs/")
        print(response.text)  # デバッグ用出力
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0


# 学習帳IDによる学習帳取得のテスト
@pytest.mark.asyncio
async def test_get_output_by_id(session: AsyncSession) -> None:
    user_id = await get_user_id(session)

    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        outputs = {
            "output": "テストマークダウン絵文字",
            "user_id": user_id,
            "created_at": "2024-06-08T06:38:33.149Z",
            "id": 0
        }
        upload_response = await client.post(
            f"/outputs/upload?user_id={user_id}", json=outputs
        )
        print(upload_response.text)  # デバッグ用出力
        assert upload_response.status_code == 200
        upload_data = upload_response.json()
        output_id = upload_data["id"]

        response = await client.get(f"/outputs/{output_id}")
        print(response.text)  # デバッグ用出力
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == output_id
        assert data["output"] == "テストマークダウン絵文字"


# 学習帳削除のテスト
@pytest.mark.asyncio
async def test_delete_output(session: AsyncSession) -> None:
    user_id = await get_user_id(session)

    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        outputs = {
            "output": "テストマークダウン絵文字",
            "user_id": user_id,
            "created_at": "2024-06-08T06:38:33.149Z",
            "id": 0
        }

        upload_response = await client.post(
            f"/outputs/upload?user_id={user_id}", json=outputs
        )
        print(upload_response.text)  # デバッグ用出力
        assert upload_response.status_code == 200
        upload_data = upload_response.json()
        output_id = upload_data["id"]

        response = await client.delete(f"/outputs/{output_id}")
        print(response.text)  # デバッグ用出力
        assert response.status_code == 200
        data = response.json()
        assert data["detail"] == "学習帳が削除されました"


# 存在しない学習帳IDによる学習帳取得のテスト
@pytest.mark.asyncio
async def test_get_output_by_id_not_found(session: AsyncSession) -> None:
    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        response = await client.get("/outputs/9999")
        print(response.text)  # デバッグ用出力
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "学習帳が見つかりません"


# 存在しない学習帳IDによる学習帳削除のテスト
@pytest.mark.asyncio
async def test_delete_output_not_found(session: AsyncSession) -> None:
    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        response = await client.delete("/outputs/9999")
        print(response.text)  # デバッグ用出力
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "学習帳が見つかりません"
