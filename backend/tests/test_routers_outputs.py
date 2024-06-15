from typing import AsyncGenerator

import pytest
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from unittest.mock import patch, AsyncMock, Mock
from fastapi import FastAPI
from pytest import MonkeyPatch
from app.main import app
from app.models.users import User
from app.routers.outputs import router
from google.api_core.exceptions import GoogleAPIError, InvalidArgument, NotFound

# .envから環境変数を読み込む
load_dotenv()

# FastAPIアプリケーションにルーターを追加
app = FastAPI()
app.include_router(router)


# 環境変数を設定するフィクスチャ
@pytest.fixture
def mock_env_vars(monkeypatch: MonkeyPatch) -> None:
    # 環境変数を設定
    monkeypatch.setenv("PROJECT_ID", "your_project_id")
    monkeypatch.setenv("REGION", "your_region")


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
        "output": "テストマークダウン🚀",
        "user_id": user_id,
        "created_at": "2024-06-08T06:38:33.149Z",
        "id": 0,
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
        assert data["output"] == "テストマークダウン🚀"


# 学習帳一覧取得のテスト
@pytest.mark.asyncio
async def test_get_outputs(session: AsyncSession) -> None:
    user_id = await get_user_id(session)

    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        outputs = {
            "output": "テストマークダウン🚀",
            "user_id": user_id,
            "created_at": "2024-06-08T06:38:33.149Z",
            "id": 0,
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
            "output": "テストマークダウン🚀",
            "user_id": user_id,
            "created_at": "2024-06-08T06:38:33.149Z",
            "id": 0,
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
        assert data["output"] == "テストマークダウン🚀"


# 学習帳削除のテスト
@pytest.mark.asyncio
async def test_delete_output(session: AsyncSession) -> None:
    user_id = await get_user_id(session)

    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        outputs = {
            "output": "テストマークダウン🚀",
            "user_id": user_id,
            "created_at": "2024-06-08T06:38:33.149Z",
            "id": 0,
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


# 正常にコンテンツが生成される場合のテスト
@pytest.mark.asyncio
@patch("app.routers.outputs.generate_content", new_callable=AsyncMock)
async def test_request_content_success(
    mock_generate_content: Mock, mock_env_vars: None
) -> None:
    # フィクスチャを適用
    mock_env_vars

    mock_generate_content.return_value = "生成されたコンテンツ"

    transport = ASGITransport(app=app)  # type: ignore
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/outputs/request", json=["file1.pdf", "file2.pdf"])

    assert response.status_code == 200
    assert response.json() == "生成されたコンテンツ"
    mock_generate_content.assert_called_once_with(["file1.pdf", "file2.pdf"])


# 指定されたファイルが見つからない場合のテスト
@pytest.mark.asyncio
@patch("app.routers.outputs.generate_content", new_callable=AsyncMock)
async def test_request_content_file_not_found(
    mock_generate_content: Mock, mock_env_vars: None
) -> None:
    # フィクスチャを適用
    mock_env_vars
    mock_generate_content.side_effect = NotFound("File not found")

    transport = ASGITransport(app=app)  # type: ignore
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/outputs/request", json=["non_existent_file.pdf"])

    assert response.status_code == 404
    assert response.json() == {
        "detail": "指定されたファイルがGoogle Cloud Storageに見つかりません。"
        + "ファイル名を再確認してください。"
    }


# 無効なファイル形式が指定された場合のテスト
@pytest.mark.asyncio
@patch("app.routers.outputs.generate_content", new_callable=AsyncMock)
async def test_request_content_invalid_argument(
    mock_generate_content: Mock, mock_env_vars: None
) -> None:
    # フィクスチャを適用
    mock_env_vars
    mock_generate_content.side_effect = InvalidArgument("Invalid file format")

    transport = ASGITransport(app=app)  # type: ignore
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/outputs/request", json=["invalid_format.txt"])

    assert response.status_code == 400
    assert response.json() == {
        "detail": "ファイル名の形式が無効です。有効なファイル名を指定してください。"
    }


# Google APIエラーが発生した場合のテスト
@pytest.mark.asyncio
@patch("app.routers.outputs.generate_content", new_callable=AsyncMock)
async def test_request_content_google_api_error(
    mock_generate_content: Mock, mock_env_vars: None
) -> None:
    # フィクスチャを適用
    mock_env_vars
    mock_generate_content.side_effect = GoogleAPIError("Google API error")

    transport = ASGITransport(app=app)  # type: ignore
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/outputs/request", json=["file1.pdf", "file2.pdf"])

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Google APIからエラーが返されました。"
        + "システム管理者に連絡してください。"
    }


# 予期せぬエラーが発生した場合のテスト
@pytest.mark.asyncio
@patch("app.routers.outputs.generate_content", new_callable=AsyncMock)
async def test_request_content_unexpected_error(
    mock_generate_content: Mock, mock_env_vars: None
) -> None:
    # フィクスチャを適用
    mock_env_vars
    mock_generate_content.side_effect = Exception("Unexpected error")

    transport = ASGITransport(app=app)  # type: ignore
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/outputs/request", json=["file1.pdf", "file2.pdf"])

    assert response.status_code == 500
    assert response.json() == {
        "detail": "コンテンツの生成中に予期せぬエラーが発生しました。"
        + "システム管理者に連絡してください。"
    }
