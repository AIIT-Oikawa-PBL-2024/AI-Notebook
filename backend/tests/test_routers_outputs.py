import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock, Mock
from fastapi import FastAPI
from pytest import MonkeyPatch
from app.routers.outputs import router
from google.api_core.exceptions import GoogleAPIError, InvalidArgument, NotFound

# FastAPIアプリケーションにルーターを追加
app = FastAPI()
app.include_router(router)


# 環境変数を設定するフィクスチャ
@pytest.fixture
def mock_env_vars(monkeypatch: MonkeyPatch) -> None:
    # 環境変数を設定
    monkeypatch.setenv("PROJECT_ID", "your_project_id")
    monkeypatch.setenv("REGION", "your_region")


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
