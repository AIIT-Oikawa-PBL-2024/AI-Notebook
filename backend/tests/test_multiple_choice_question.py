from typing import Generator, Tuple
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from google.api_core.exceptions import GoogleAPIError, InternalServerError
import base64

from app.utils.multiple_choice_question import (
    check_file_exists,
    read_file,
    extract_text_from_pdf,
    generate_content_json,
)

# Test data
MOCK_BUCKET_NAME = "test-bucket"
MOCK_PROJECT_ID = "test-project"
MOCK_REGION = "europe-west1"
MOCK_MODEL_NAME = "claude-3-sonnet-20240620"  # 実際のモデル名のフォーマットに合わせる
MOCK_UID = "test_user"

# Mock response from Anthropic API
MOCK_ANTHROPIC_RESPONSE = {
    "content": [
        {
            "type": "tool_calls",
            "tool_calls": [
                {
                    "id": "test_id",
                    "type": "function",
                    "function": {
                        "name": "print_multiple_choice_questions",
                        "arguments": {
                            "questions": [
                                {
                                    "question_id": "question_1",
                                    "question_text": "Test question?",
                                    "choices": {
                                        "choice_a": "Test A",
                                        "choice_b": "Test B",
                                        "choice_c": "Test C",
                                        "choice_d": "Test D",
                                    },
                                    "answer": "choice_a",
                                    "explanation": "Test explanation",
                                }
                            ]
                        },
                    },
                }
            ],
        }
    ]
}


@pytest.fixture(autouse=True)
def mock_env_vars() -> Generator[None, None, None]:
    """Mock environment variables - automatically used in all tests"""
    with patch.dict(
        "os.environ",
        {
            "PROJECT_ID": MOCK_PROJECT_ID,
            "BUCKET_NAME": MOCK_BUCKET_NAME,
            "REGION": MOCK_REGION,
        },
    ):
        yield


@pytest.fixture
def mock_storage_client() -> Generator[Tuple[MagicMock, MagicMock], None, None]:
    """Mock Google Cloud Storage client"""
    with patch("app.utils.multiple_choice_question.storage.Client") as mock_client:
        mock_blob = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.return_value.bucket.return_value = mock_bucket
        yield mock_client, mock_blob


@pytest.fixture
def mock_anthropic_client() -> Generator[MagicMock, None, None]:
    """Mock Anthropic client"""
    with patch("app.utils.multiple_choice_question.AnthropicVertex") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.messages.create.return_value = MagicMock(
            to_dict=lambda: MOCK_ANTHROPIC_RESPONSE
        )
        yield mock_client


@pytest.fixture(autouse=True)
def mock_fitz() -> Generator[MagicMock, None, None]:
    """Mock PyMuPDF (fitz) for PDF processing - automatically used in all tests"""
    with patch("app.utils.multiple_choice_question.fitz.open") as mock_fitz:
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Test PDF content"
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz.return_value = mock_doc
        yield mock_fitz


@pytest.mark.asyncio
async def test_generate_content_json_internal_server_error(
    mock_storage_client: Tuple[MagicMock, MagicMock],
) -> None:
    """Test generate_content_json when internal server error occurs"""
    mock_client, mock_blob = mock_storage_client
    mock_blob.exists.return_value = True
    mock_blob.download_as_bytes.return_value = b"test content"

    with patch("app.utils.multiple_choice_question.AnthropicVertex") as mock_anthropic:
        mock_instance = mock_anthropic.return_value
        mock_instance.messages.create.side_effect = InternalServerError("Internal Server Error")

        with pytest.raises(InternalServerError):
            await generate_content_json(
                files=["test.pdf"],
                uid=MOCK_UID,
                title="Test title",
                difficulty="easy",
                model_name=MOCK_MODEL_NAME,
                bucket_name=MOCK_BUCKET_NAME,
            )


@pytest.mark.asyncio
async def test_check_file_exists_true(
    mock_storage_client: Tuple[MagicMock, MagicMock],
) -> None:
    """Test check_file_exists when file exists"""
    mock_client, mock_blob = mock_storage_client
    mock_blob.exists.return_value = True

    result = await check_file_exists(MOCK_BUCKET_NAME, "test.pdf")

    assert result is True
    mock_client.return_value.bucket.assert_called_once_with(MOCK_BUCKET_NAME)
    mock_blob.exists.assert_called_once()


@pytest.mark.asyncio
async def test_check_file_exists_false(
    mock_storage_client: Tuple[MagicMock, MagicMock],
) -> None:
    """Test check_file_exists when file does not exist"""
    mock_client, mock_blob = mock_storage_client
    mock_blob.exists.return_value = False

    result = await check_file_exists(MOCK_BUCKET_NAME, "nonexistent.pdf")

    assert result is False


@pytest.mark.asyncio
async def test_read_file(
    mock_storage_client: Tuple[MagicMock, MagicMock],
) -> None:
    """Test read_file function"""
    mock_client, mock_blob = mock_storage_client
    test_content = b"test content"

    # download_as_bytesの戻り値を設定
    mock_blob.download_as_bytes.return_value = test_content

    result = await read_file(MOCK_BUCKET_NAME, "test.png")

    expected_base64 = base64.b64encode(test_content).decode("utf-8")
    assert result == expected_base64


@pytest.mark.asyncio
async def test_extract_text_from_pdf(
    mock_storage_client: Tuple[MagicMock, MagicMock],
) -> None:
    """Test extract_text_from_pdf function"""
    mock_client, mock_blob = mock_storage_client
    mock_blob.download_as_bytes.return_value = b"mock pdf content"

    result = await extract_text_from_pdf(MOCK_BUCKET_NAME, "test.pdf")

    assert "Test PDF content" in result
    mock_blob.download_as_bytes.assert_called_once()


@pytest.mark.asyncio
async def test_generate_content_json_pdf(
    mock_storage_client: Tuple[MagicMock, MagicMock],
) -> None:
    """Test generate_content_json with PDF file"""
    mock_client, mock_blob = mock_storage_client
    mock_blob.exists.return_value = True
    mock_blob.download_as_bytes.return_value = b"mock pdf content"

    with patch("app.utils.multiple_choice_question.AnthropicVertex") as mock_anthropic:
        mock_instance = mock_anthropic.return_value
        mock_instance.messages.create.return_value = MagicMock(
            to_dict=lambda: MOCK_ANTHROPIC_RESPONSE
        )

        result = await generate_content_json(
            files=["test.pdf"],
            uid=MOCK_UID,
            title="Test title",
            difficulty="easy",
            model_name=MOCK_MODEL_NAME,
            bucket_name=MOCK_BUCKET_NAME,
        )

        assert result == MOCK_ANTHROPIC_RESPONSE
        mock_blob.exists.assert_called_once()
        mock_blob.download_as_bytes.assert_called_once()
        mock_instance.messages.create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_content_json_image(
    mock_storage_client: Tuple[MagicMock, MagicMock],
) -> None:
    """Test generate_content_json with image file"""
    mock_client, mock_blob = mock_storage_client
    mock_blob.exists.return_value = True
    test_content = b"test image content"
    mock_blob.download_as_bytes.return_value = test_content

    with patch("app.utils.multiple_choice_question.AnthropicVertex") as mock_anthropic:
        mock_instance = mock_anthropic.return_value
        mock_instance.messages.create.return_value = MagicMock(
            to_dict=lambda: MOCK_ANTHROPIC_RESPONSE
        )

        result = await generate_content_json(
            files=["test.png"],
            uid=MOCK_UID,
            title="Test title",
            difficulty="easy",
            model_name=MOCK_MODEL_NAME,
            bucket_name=MOCK_BUCKET_NAME,
        )

        assert result == MOCK_ANTHROPIC_RESPONSE
        mock_blob.exists.assert_called_once()
        mock_instance.messages.create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_content_json_file_not_found(
    mock_storage_client: Tuple[MagicMock, MagicMock],
) -> None:
    """Test generate_content_json when file does not exist"""
    mock_client, mock_blob = mock_storage_client
    mock_blob.exists.return_value = False

    with pytest.raises(Exception):
        await generate_content_json(
            files=["nonexistent.pdf"],
            uid=MOCK_UID,
            title="Test title",
            difficulty="easy",
            model_name=MOCK_MODEL_NAME,
            bucket_name=MOCK_BUCKET_NAME,
        )


@pytest.mark.asyncio
async def test_generate_content_json_google_api_error(
    mock_storage_client: Tuple[MagicMock, MagicMock],
) -> None:
    """Test generate_content_json when Google API error occurs"""
    mock_client, mock_blob = mock_storage_client
    mock_blob.exists.side_effect = GoogleAPIError("API Error")

    with pytest.raises(GoogleAPIError):
        await generate_content_json(
            files=["test.pdf"],
            uid=MOCK_UID,
            title="Test title",
            difficulty="easy",
            model_name=MOCK_MODEL_NAME,
            bucket_name=MOCK_BUCKET_NAME,
        )
