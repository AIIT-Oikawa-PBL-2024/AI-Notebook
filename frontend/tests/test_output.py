import pytest
import httpx
from unittest.mock import patch, AsyncMock, MagicMock
from pytest_httpx import HTTPXMock, IteratorStream
import os
from dotenv import load_dotenv

from app.utils.output import (
    fetch_gemini_stream_data,
    create_pdf_to_markdown_summary,
)


load_dotenv()

BACKEND_HOST = os.getenv("BACKEND_DEV_HOST")


@pytest.mark.asyncio
async def test_fetch_gemini_stream_data(httpx_mock: HTTPXMock) -> None:
    BACKEND_DEV_API_URL = f"{BACKEND_HOST}/outputs/request_stream/"

    filenames = ["test.pdf"]
    httpx_mock.add_response(
        method="POST",
        url=BACKEND_DEV_API_URL,
        stream=IteratorStream([b"*Test Output*"]),
        status_code=200,
        json=filenames,
    )

    async with httpx.AsyncClient() as client:
        async with client.stream(
            method="POST", url=BACKEND_DEV_API_URL, json=filenames
        ) as response:
            assert [part async for part in response.aiter_raw()] == [b"*Test Output*"]


@pytest.mark.asyncio
async def test_fetch_gemini_stream_data_success(httpx_mock: HTTPXMock) -> None:
    BACKEND_DEV_API_URL = f"{BACKEND_HOST}/outputs/request_stream/"
    filenames = ["test.pdf"]

    httpx_mock.add_response(
        method="POST",
        url=BACKEND_DEV_API_URL,
        stream=IteratorStream([b"chunk1", b"chunk2"]),
        status_code=200,
        headers={"accept": "text/event-stream"},
        json=filenames,
    )

    data = []
    async for chunk in fetch_gemini_stream_data(filenames):
        data.append(chunk)

    assert data == ["chunk1", "chunk2"]


@pytest.mark.asyncio
async def test_fetch_gemini_stream_data_http_error(httpx_mock: HTTPXMock) -> None:
    BACKEND_DEV_API_URL = f"{BACKEND_HOST}/outputs/request_stream/"
    filenames = ["test.pdf"]

    httpx_mock.add_exception(
        exception=httpx.HTTPStatusError(
            "エラーが発生しました",
            request=httpx.Request(
                "POST",
                BACKEND_DEV_API_URL,
                stream=IteratorStream([b"chunk1", b"chunk2"]),
                json=filenames,
                headers={"accept": "text/event-stream"},
            ),
            response=httpx.Response(400),
        ),
    )

    async with httpx.AsyncClient() as client:
        with pytest.raises(httpx.HTTPStatusError):
            async with client.stream(
                method="POST", url=BACKEND_DEV_API_URL, json=filenames
            ):
                pass


@pytest.mark.asyncio
async def test_fetch_gemini_stream_data_remote_protocol_error(
    httpx_mock: HTTPXMock,
) -> None:
    BACKEND_DEV_API_URL = f"{BACKEND_HOST}/outputs/request_stream/"
    filenames = ["test.pdf"]

    httpx_mock.add_exception(
        exception=httpx.RemoteProtocolError(
            "通信中にエラーが発生しました",
            request=httpx.Request(
                "POST",
                BACKEND_DEV_API_URL,
                stream=IteratorStream([b"chunk1", b"chunk2"]),
                json=filenames,
                headers={"accept": "text/event-stream"},
            ),
        ),
    )

    async with httpx.AsyncClient() as client:
        with pytest.raises(httpx.RemoteProtocolError):
            async with client.stream(
                method="POST", url=BACKEND_DEV_API_URL, json=filenames
            ):
                pass


@pytest.mark.asyncio
async def test_fetch_gemini_stream_data_request_error(httpx_mock: HTTPXMock) -> None:
    BACKEND_DEV_API_URL = f"{BACKEND_HOST}/outputs/request_stream/"
    filenames = ["test.pdf"]

    httpx_mock.add_exception(
        exception=httpx.RequestError(
            "リクエストエラーが発生しました",
            request=httpx.Request(
                "POST",
                BACKEND_DEV_API_URL,
                stream=IteratorStream([b"chunk1", b"chunk2"]),
                json=filenames,
                headers={"accept": "text/event-stream"},
            ),
        ),
    )

    async with httpx.AsyncClient() as client:
        with pytest.raises(httpx.RequestError):
            async with client.stream(
                method="POST", url=BACKEND_DEV_API_URL, json=filenames
            ):
                pass


@pytest.mark.asyncio
async def test_fetch_gemini_stream_data_timeout_error(httpx_mock: HTTPXMock) -> None:
    BACKEND_DEV_API_URL = f"{BACKEND_HOST}/outputs/request_stream/"
    filenames = ["test.pdf"]

    httpx_mock.add_exception(
        exception=httpx.TimeoutException(
            "タイムアウトしました",
            request=httpx.Request(
                "POST",
                BACKEND_DEV_API_URL,
                stream=IteratorStream([b"chunk1", b"chunk2"]),
                json=filenames,
                headers={"accept": "text/event-stream"},
            ),
        ),
    )

    async with httpx.AsyncClient() as client:
        with pytest.raises(httpx.TimeoutException):
            async with client.stream(
                method="POST", url=BACKEND_DEV_API_URL, json=filenames
            ):
                pass


@pytest.mark.asyncio
async def test_fetch_gemini_stream_data_exception_error(httpx_mock: HTTPXMock) -> None:
    BACKEND_DEV_API_URL = f"{BACKEND_HOST}/outputs/request_stream/"
    filenames = ["test.pdf"]

    httpx_mock.add_exception(
        exception=Exception(),
    )

    async with httpx.AsyncClient() as client:
        with pytest.raises(Exception):
            async with client.stream(
                method="POST", url=BACKEND_DEV_API_URL, json=filenames
            ):
                pass


@pytest.mark.asyncio
async def test_create_pdf_to_markdown_summary(httpx_mock: HTTPXMock) -> None:
    BACKEND_DEV_API_URL = f"{BACKEND_HOST}/outputs/request_stream/"
    filenames = ["test.pdf"]

    httpx_mock.add_response(
        method="POST",
        url=BACKEND_DEV_API_URL,
        stream=IteratorStream([b"chunk1"]),
        status_code=200,
        headers={"accept": "text/event-stream"},
        json=filenames,
    )

    with patch("streamlit.empty") as empty_mock:
        empty_mock.return_value = output = MagicMock()
        output.markdown = MagicMock()

        await create_pdf_to_markdown_summary(filenames)

        empty_mock.assert_called_once()
        output.markdown.assert_called_once_with("chunk1")
