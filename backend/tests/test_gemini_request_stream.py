import pytest
from unittest.mock import AsyncMock, patch, Mock
from google.api_core.exceptions import GoogleAPIError, InvalidArgument, NotFound
from app.utils.gemini_request_stream import generate_content_stream
from pytest import MonkeyPatch
import json
from typing import Generator
from vertexai.generative_models import GenerationConfig


# 環境変数を設定するフィクスチャ
@pytest.fixture
def mock_env_vars(monkeypatch: MonkeyPatch) -> None:
    # 環境変数を設定
    monkeypatch.setenv("PROJECT_ID", "your_project_id")
    monkeypatch.setenv("REGION", "your_region")
    monkeypatch.setenv("BUCKET_NAME", "your_bucket_name")


# 正常系のテスト
@patch("app.utils.gemini_request_stream.GenerativeModel", autospec=True)
@pytest.mark.asyncio
async def test_generate_content_stream_success(
    mock_GenerativeModel: Mock, mock_env_vars: None
) -> None:
    # フィクスチャを適用
    mock_env_vars

    # モックレスポンスの設定
    def mock_generate_content(
        contents: list, generation_config: GenerationConfig, stream: bool = True
    ) -> Generator:
        responses = [
            {
                "candidates": [
                    {"content": {"parts": [{"text": "Sample content part 1"}]}}
                ]
            },
            {
                "candidates": [
                    {"content": {"parts": [{"text": "Sample content part 2"}]}}
                ]
            },
        ]
        for response in responses:
            yield response

    mock_GenerativeModel.return_value.generate_content.side_effect = (
        lambda contents, generation_config, stream: mock_generate_content(
            contents, generation_config, stream
        )
    )

    # テスト対象関数の実行
    result = generate_content_stream(["file1.pdf", "file2.pdf"])

    accumulated_content = []
    async for content in result:
        content_dict = content
        json_string = json.dumps(content_dict)
        data = json.loads(json_string)
        text_value = data["candidates"][0]["content"]["parts"][0]["text"]
        accumulated_content.append(text_value)

    assert "Sample content part 1" in accumulated_content
    assert "Sample content part 2" in accumulated_content


# ファイルが見つからない場合のエラーハンドリングのテスト
@patch("app.utils.gemini_request_stream.GenerativeModel", autospec=True)
@pytest.mark.asyncio
async def test_generate_content_stream_not_found(
    mock_GenerativeModel: Mock, mock_env_vars: None
) -> None:
    # フィクスチャを適用
    mock_env_vars
    mock_GenerativeModel.return_value.generate_content.side_effect = NotFound(
        "File not found"
    )

    # テスト対象関数の実行とエラーハンドリングの確認
    with pytest.raises(NotFound) as excinfo:
        result = generate_content_stream(["non_existent_file.pdf"])
        async for _ in result:
            pass
    assert str(excinfo.value) == "404 File not found"


# 無効な引数の場合のエラーハンドリングのテスト
@patch("app.utils.gemini_request_stream.GenerativeModel", autospec=True)
@pytest.mark.asyncio
async def test_generate_content_stream_invalid_argument(
    mock_GenerativeModel: Mock, mock_env_vars: None
) -> None:
    # フィクスチャを適用
    mock_env_vars
    mock_GenerativeModel.return_value.generate_content.side_effect = InvalidArgument(
        "Invalid file format"
    )

    # テスト対象関数の実行とエラーハンドリングの確認
    with pytest.raises(InvalidArgument) as excinfo:
        result = generate_content_stream(["invalid_file"])
        async for _ in result:
            pass
    assert str(excinfo.value) == "400 Invalid file format"


# Google APIエラーの場合のエラーハンドリングのテスト
@patch("app.utils.gemini_request_stream.GenerativeModel", autospec=True)
@pytest.mark.asyncio
async def test_generate_content_stream_google_api_error(
    mock_GenerativeModel: Mock, mock_env_vars: None
) -> None:
    # フィクスチャを適用
    mock_env_vars
    mock_GenerativeModel.return_value.generate_content.side_effect = GoogleAPIError(
        "Google API error"
    )

    # テスト対象関数の実行とエラーハンドリングの確認
    with pytest.raises(GoogleAPIError) as excinfo:
        result = generate_content_stream(["file1.pdf"])
        async for _ in result:
            pass
    assert str(excinfo.value) == "Google API error"


# その他の予期しないエラーの場合のエラーハンドリングのテスト
@patch("app.utils.gemini_request_stream.GenerativeModel", autospec=True)
@pytest.mark.asyncio
async def test_generate_content_stream_unexpected_error(
    mock_GenerativeModel: Mock, mock_env_vars: None
) -> None:
    # フィクスチャを適用
    mock_env_vars
    mock_GenerativeModel.return_value.generate_content.side_effect = Exception(
        "Unexpected error"
    )

    # テスト対象関数の実行とエラーハンドリングの確認
    with pytest.raises(Exception) as excinfo:
        result = generate_content_stream(["file1.pdf"])
        async for _ in result:
            pass
    assert str(excinfo.value) == "Unexpected error"


# エラーハンドリングのテスト（モデル属性エラー）
@patch("app.utils.gemini_request_stream.GenerativeModel", autospec=True)
@pytest.mark.asyncio
async def test_generate_content_stream_attribute_error(
    mock_GenerativeModel: Mock, mock_env_vars: None
) -> None:
    # フィクスチャを適用
    mock_env_vars
    mock_GenerativeModel.return_value.generate_content.side_effect = AttributeError(
        "Model attribute error"
    )

    # テスト対象関数の実行とエラーハンドリングの確認
    with pytest.raises(AttributeError) as excinfo:
        result = generate_content_stream(["file1.pdf", "file2.pdf"])
        async for _ in result:
            pass
    assert str(excinfo.value) == "Model attribute error"


# エラーハンドリングのテスト（タイプエラー）
@patch("app.utils.gemini_request_stream.GenerativeModel", autospec=True)
@pytest.mark.asyncio
async def test_generate_content_stream_type_error(
    mock_GenerativeModel: Mock, mock_env_vars: None
) -> None:
    # フィクスチャを適用
    mock_env_vars
    mock_GenerativeModel.return_value.generate_content.side_effect = TypeError(
        "Type error in model generation"
    )

    # テスト対象関数の実行とエラーハンドリングの確認
    with pytest.raises(TypeError) as excinfo:
        result = generate_content_stream(["file1.pdf", "file2.pdf"])
        async for _ in result:
            pass
    assert str(excinfo.value) == "Type error in model generation"