import json
from typing import Generator, Tuple
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from google.api_core.exceptions import GoogleAPIError, InternalServerError

from app.utils.user_answer import (
    generate_scoring_result_json,
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
                        "name": "print_user_answers",
                        "arguments": {
                            "questions": [
                                {
                                    "question_id": "question_1",
                                    "scoring_result": "Test result",
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
def mock_anthropic_client() -> Generator[MagicMock, None, None]:
    """Mock Anthropic client"""
    with patch("app.utils.essay_question.AnthropicVertex") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.messages.create.return_value = MagicMock(
            to_dict=lambda: MOCK_ANTHROPIC_RESPONSE
        )
        yield mock_client


@pytest.mark.asyncio
async def test_generate_scoring_result_json_internal_server_error() -> None:
    """Test generate_scoring_result_json when internal server error occurs"""

    with patch("app.utils.user_answer.AnthropicVertex") as mock_anthropic:
        mock_instance = mock_anthropic.return_value
        mock_instance.messages.create.side_effect = InternalServerError("Internal Server Error")

        with pytest.raises(InternalServerError):
            await generate_scoring_result_json(
                exercise=json.dumps({"content": [{"input": {"questions": []}}]}),
                uid=MOCK_UID,
                user_answers=["test answer"],
                model_name=MOCK_MODEL_NAME,
                bucket_name=MOCK_BUCKET_NAME,
            )


@pytest.mark.asyncio
async def test_generate_scoring_result_json() -> None:
    """Test generate_scoring_result_json"""

    with patch("app.utils.user_answer.AnthropicVertex") as mock_anthropic:
        mock_instance = mock_anthropic.return_value
        mock_instance.messages.create.return_value = MagicMock(
            to_dict=lambda: MOCK_ANTHROPIC_RESPONSE
        )

        result = await generate_scoring_result_json(
            exercise=json.dumps({"content": [{"input": {"questions": []}}]}),
            uid=MOCK_UID,
            user_answers=["test answer"],
            model_name=MOCK_MODEL_NAME,
            bucket_name=MOCK_BUCKET_NAME,
        )

        assert result == MOCK_ANTHROPIC_RESPONSE
        mock_instance.messages.create.assert_called_once()
