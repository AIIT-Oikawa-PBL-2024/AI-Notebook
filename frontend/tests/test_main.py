import os
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
import pytest
from dotenv import load_dotenv
from streamlit.testing.v1 import AppTest

from app.main import upload_files_and_get_response, is_valid_file


def test_file_uploader() -> None:
    "Streamlitのfile_uploaderが複数ファイルをアップロードできることをテストします。"
    at = AppTest.from_file("app/main.py").run()
    file_uploader = at.get("file_uploader")[0]
    assert file_uploader.multiple_files is True  # type: ignore


def test_is_valid_file_success() -> None:
    "is_valid_file関数が失敗することをテストします。"
    # Create a mock file
    mock_file = MagicMock()
    mock_file.name = "test.pdf"
    mock_file.type = "application/pdf"

    # Test the function with a valid file
    assert is_valid_file(mock_file) is True


def test_is_valid_file_failed() -> None:
    "is_valid_file関数が成功することをテストします。"
    # Create a mock file
    mock_file = MagicMock()
    mock_file.name = "test.txt"
    mock_file.type = "text/plain"

    # Test the function with a valid file
    assert is_valid_file(mock_file) is False


@pytest.mark.asyncio
async def test_upload_files_and_get_response_success() -> None:
    "upload_files_and_get_response関数が成功することをテストします。"
    mock_file = MagicMock()
    mock_file.name = "test.pdf"
    mock_file.type = "application/pdf"

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "success": True,
        "success_files": [{"filename": "test.pdf", "message": "Successfully uploaded"}],
        "failed_files": [],
    }

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post.return_value = (
            mock_response
        )
        result = await upload_files_and_get_response([mock_file])

        assert result["success"] == True
        assert "success_files" in result
        assert "failed_files" in result
        assert len(result["success_files"]) == 1
        assert result["success_files"][0]["filename"] == "test.pdf"


@pytest.mark.asyncio
async def test_upload_files_and_get_response_failure() -> None:
    "upload_files_and_get_response関数が失敗することをテストします。"
    # Create pdf mockfile
    mock_file = MagicMock()
    mock_file.name = "test.pdf"
    mock_file.type = "application/pdf"

    # Mock httpx.AsyncClient.post to raise an exception
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.RequestError("An error occurred.")

        # Execute the function and catch the exception
        result = await upload_files_and_get_response([mock_file])

        # Verify the error message
        assert "error" in result
