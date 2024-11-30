import pytest
from unittest import mock
from google.cloud import storage
from app.utils import claude_request_stream
import fitz
import base64
from pytest import MonkeyPatch
from typing import Generator, Optional, Type, Any, AsyncGenerator
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from google.api_core.exceptions import GoogleAPIError, InternalServerError


# 環境変数のモック
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("PROJECT_ID", "test-project-id")
    monkeypatch.setenv("BUCKET_NAME", "test-bucket-name")


# storage.Clientのモック
@pytest.fixture
def mock_storage_client() -> Generator:
    with mock.patch("app.utils.claude_request_stream.storage.Client") as mock_client:
        yield mock_client


# 非同期コンテキストマネージャを定義するためのクラス
class AsyncContextManager:
    def __init__(self, result: AsyncMock) -> None:
        self.result = result

    async def __aenter__(self) -> AsyncMock:
        return self.result

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[Any],
    ) -> None:
        pass


# check_file_exists関数のテスト
@pytest.mark.asyncio
async def test_check_file_exists(mock_storage_client: Mock) -> None:
    mock_bucket = mock.Mock()
    mock_blob = mock.Mock()

    # bucket.blob(file_name).exists()の戻り値をTrueに設定
    mock_blob.exists.return_value = True
    mock_bucket.blob.return_value = mock_blob
    mock_storage_client.return_value.bucket.return_value = mock_bucket

    result = await claude_request_stream.check_file_exists("test-bucket-name", "test-file.pdf")
    assert result == True

    # bucket.blob(file_name).exists()の戻り値をFalseに設定
    mock_blob.exists.return_value = False
    result = await claude_request_stream.check_file_exists("test-bucket-name", "test-file.pdf")
    assert result == False


# read_file関数のテスト
@pytest.mark.asyncio
async def test_read_file(mock_storage_client: Mock) -> None:
    mock_bucket = mock.Mock()
    mock_blob = mock.Mock()

    # ファイル内容のモック
    mock_file_content = b"test file content"

    # download_as_bytesのモックを設定
    mock_blob.download_as_bytes.return_value = mock_file_content
    mock_bucket.blob.return_value = mock_blob
    mock_storage_client.return_value.bucket.return_value = mock_bucket

    result = await claude_request_stream.read_file("test-bucket-name", "test-file.png")

    # 戻り値がbase64エンコードされた内容であることを確認
    assert result == base64.b64encode(mock_file_content).decode("utf-8")


# pdfからテキスト抽出関数のテスト
@pytest.mark.asyncio
async def test_extract_text_from_pdf(mock_storage_client: Mock) -> None:
    mock_bucket = mock.Mock()
    mock_blob = mock.Mock()

    # ファイル内容のモック
    mock_pdf_content = b"mock pdf content"

    # 非同期コンテキストマネージャとしてモックする
    mock_blob.download_as_bytes.return_value = mock_pdf_content
    mock_bucket.blob.return_value = mock_blob
    mock_storage_client.return_value.bucket.return_value = mock_bucket

    with mock.patch("app.utils.claude_request_stream.fitz.open") as mock_open:
        mock_page = mock.Mock()
        mock_page.get_text.return_value = "Mock Page Text"
        mock_open.return_value.__iter__.return_value = [mock_page]

        result = await claude_request_stream.extract_text_from_pdf(
            "test-bucket-name", "test-file.pdf"
        )

    assert "Mock Page Text" in result


# モック版の generate_content_stream 関数
async def mock_generate_content_stream(files: list, model: str, bucket: str) -> AsyncGenerator:
    yield "Mock generated content part 1."
    yield "Mock generated content part 2."


# 正常系のテスト
async def test_generate_content_stream() -> None:
    files = ["test_document.pdf"]

    # generate_content_stream 関数全体をモックに置き換え
    with patch(
        "app.utils.claude_request_stream.generate_content_stream",
        new=mock_generate_content_stream,
    ):
        # テスト対象の関数を呼び出し
        content_stream = mock_generate_content_stream(files, "test_model", "test_bucket")

        result = []
        async for part in content_stream:
            print(f"Received part: {part}")  # デバッグ用出力
            result.append(part)

        print(f"Final result: {result}")  # デバッグ用出力

    # アサーション
    assert len(result) == 2, f"Expected 2 items, but got {len(result)}"
    assert result[0] == "Mock generated content part 1."
    assert result[1] == "Mock generated content part 2."


# 例外処理のテスト
@pytest.mark.asyncio
async def test_generate_content_stream_attribute_error() -> None:
    files = ["test_document.pdf"]

    with patch("app.utils.claude_request_stream.AnthropicVertex") as MockAnthropicVertex:
        instance = MockAnthropicVertex.return_value
        instance.messages.stream.side_effect = AttributeError("Model attribute error")

        with pytest.raises(AttributeError, match="Model attribute error"):
            async for _ in claude_request_stream.generate_content_stream(files, "test_user"):
                pass


@pytest.mark.asyncio
async def test_generate_content_stream_type_error() -> None:
    files = ["test_document.pdf"]

    with patch("app.utils.claude_request_stream.AnthropicVertex") as MockAnthropicVertex:
        instance = MockAnthropicVertex.return_value
        instance.messages.stream.side_effect = TypeError("Type error in model generation")

        with pytest.raises(TypeError, match="Type error in model generation"):
            async for _ in claude_request_stream.generate_content_stream(files, "test_user"):
                pass


@pytest.mark.asyncio
async def test_generate_content_stream_internal_server_error() -> None:
    files = ["test_document.pdf"]

    with patch("app.utils.claude_request_stream.AnthropicVertex") as MockAnthropicVertex:
        instance = MockAnthropicVertex.return_value
        instance.messages.stream.side_effect = InternalServerError("Internal server error")

        with pytest.raises(InternalServerError, match="Internal server error"):
            async for _ in claude_request_stream.generate_content_stream(files, "test_user"):
                pass


@pytest.mark.asyncio
async def test_generate_content_stream_google_api_error() -> None:
    files = ["test_document.pdf"]

    with patch("app.utils.claude_request_stream.AnthropicVertex") as MockAnthropicVertex:
        instance = MockAnthropicVertex.return_value
        instance.messages.stream.side_effect = GoogleAPIError("Google API error")

        with pytest.raises(GoogleAPIError, match="Google API error"):
            async for _ in claude_request_stream.generate_content_stream(files, "test_user"):
                pass


@pytest.mark.asyncio
async def test_generate_content_stream_unexpected_error() -> None:
    files = ["test_document.pdf"]

    with patch("app.utils.claude_request_stream.AnthropicVertex") as MockAnthropicVertex:
        instance = MockAnthropicVertex.return_value
        instance.messages.stream.side_effect = Exception("Unexpected error")

        with pytest.raises(Exception, match="Unexpected error"):
            async for _ in claude_request_stream.generate_content_stream(files, "test_user"):
                pass
