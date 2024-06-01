import os
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from dotenv import load_dotenv
from streamlit.testing.v1 import AppTest

from app.main import upload_files_and_get_response

# 環境変数のロード
load_dotenv()

# テスト用の設定
BACKEND_HOST = os.getenv("BACKEND_HOST")


def test_file_upload() -> None:
    "Test the file upload function of the app."
    at = AppTest.from_file("app/main.py").run()
    file_uploader = at.get("file_uploader")[0]
    assert file_uploader.label == "ファイルをアップロードしてください"  # type: ignore
    assert file_uploader.multiple_files is True  # type: ignore


def test_sidebar() -> None:
    "Test the sidebar of the app."
    at = AppTest.from_file("app/main.py").run()
    assert at.sidebar[0].page == "main"  # type: ignore
    assert at.sidebar[0].label == "ホーム"  # type: ignore
    assert at.sidebar[0].icon == "🏠"  # type: ignore
    assert at.sidebar[1].page == "page1"  # type: ignore
    assert at.sidebar[1].label == "マルチページ1"  # type: ignore
    assert at.sidebar[1].icon == "1️⃣"  # type: ignore
    assert at.sidebar[2].page == "page2"  # type: ignore
    assert at.sidebar[2].label == "マルチページ2"  # type: ignore
    assert at.sidebar[2].icon == "2️⃣"  # type: ignore


@pytest.mark.asyncio
async def test_upload_files_and_get_response_success() -> None:
    expected_message = {"message": "テストOK"}
    mock_file = MagicMock()
    mock_file.name = "test.txt"
    mock_file.type = "text/plain"

    # Mock httpx.AsyncClient.post
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.json = AsyncMock(return_value=expected_message)

        # Execute the function
        result = await upload_files_and_get_response([mock_file])

        # Verify the expected message
        assert await result == expected_message  # type: ignore


@pytest.mark.asyncio
async def test_upload_files_and_get_response_failure() -> None:
    mock_file = MagicMock()
    mock_file.name = "test.txt"
    mock_file.type = "text/plain"

    # Mock httpx.AsyncClient.post to raise an exception
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.RequestError("An error occurred.")

        # Execute the function and catch the exception
        result = await upload_files_and_get_response([mock_file])

        # Verify the error message
        assert "An error occurred." in result["error"]