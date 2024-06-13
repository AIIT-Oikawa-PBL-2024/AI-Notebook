import pytest
import httpx
from unittest.mock import patch, AsyncMock
from pytest_httpx import HTTPXMock, IteratorStream

from app.pages.output import display_gemini_processed_markdown


@pytest.mark.asyncio
async def test_display_gemini_processed_markdown_success(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        method="POST",
        url="https://localhost:8000/outputs/request",
        stream=IteratorStream([b"*Test Output*"]),
        status_code=200,
    )

    with patch("streamlit.empty", return_value=AsyncMock()) as mock_empty:
        placeholder = mock_empty.return_value
        await display_gemini_processed_markdown()
        placeholder.write.assert_called_once_with("*Test Output*")


@pytest.mark.asyncio
async def test_display_gemini_processed_markdown_unexpected_error(
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_exception(
        method="POST",
        url="https://localhost:8000/outputs/request",
        exception=Exception("予期せぬエラーが発生しました"),
    )

    with (
        patch("streamlit.empty", new_callable=AsyncMock) as mock_empty,
        patch("streamlit.write", new_callable=AsyncMock) as mock_write,
    ):
        placeholder = mock_empty.return_value
        await display_gemini_processed_markdown()
        mock_write.assert_called_once_with(
            "予期せぬエラーが発生しました。エラー： 予期せぬエラーが発生しました"
        )
