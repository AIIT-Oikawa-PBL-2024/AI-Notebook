import pytest
from unittest.mock import AsyncMock, patch, Mock
from google.api_core.exceptions import GoogleAPIError, InvalidArgument, NotFound
from app.utils.gemini_request_stream import generate_content_stream, check_file_exists
from pytest import MonkeyPatch
import json
from typing import Generator
from vertexai.generative_models import GenerationConfig


# 環境変数を設定するフィクスチャ
@pytest.fixture
def mock_env_vars(monkeypatch: MonkeyPatch) -> None:
    """
    環境変数を設定するフィクスチャ

    :param monkeypatch: pytestのMonkeyPatchオブジェクト
    :type monkeypatch: MonkeyPatch
    """
    # 環境変数を設定
    monkeypatch.setenv("PROJECT_ID", "your_project_id")
    monkeypatch.setenv("REGION", "your_region")
    monkeypatch.setenv("BUCKET_NAME", "your_bucket_name")


# 正常系のテスト
@patch("app.utils.gemini_request_stream.GenerativeModel", autospec=True)
@patch("app.utils.gemini_request_stream.check_file_exists", return_value=True)
@pytest.mark.asyncio
async def test_generate_content_stream_success(
    mock_check_file_exists: Mock, mock_GenerativeModel: Mock, mock_env_vars: None
) -> None:
    """
    正常系のテスト

    :param mock_check_file_exists: ファイル存在確認のモック
    :type mock_check_file_exists: Mock
    :param mock_GenerativeModel: GenerativeModelのモック
    :type mock_GenerativeModel: Mock
    :param mock_env_vars: 環境変数のモックフィクスチャ
    :type mock_env_vars: None
    """
    # フィクスチャを適用
    mock_env_vars

    # モックレスポンスの設定
    def mock_generate_content(
        contents: list, generation_config: GenerationConfig, stream: bool = True
    ) -> Generator:
        """
        モックのコンテンツ生成関数

        :param contents: コンテンツのリスト
        :type contents: list
        :param generation_config: GenerationConfigオブジェクト
        :type generation_config: GenerationConfig
        :param stream: ストリーミングフラグ
        :type stream: bool
        :return: コンテンツのジェネレータ
        :rtype: Generator
        """
        responses = [
            {"candidates": [{"content": {"parts": [{"text": "Sample content part 1"}]}}]},
            {"candidates": [{"content": {"parts": [{"text": "Sample content part 2"}]}}]},
        ]
        for response in responses:
            yield response

    mock_GenerativeModel.return_value.generate_content.side_effect = (
        lambda contents, generation_config, stream: mock_generate_content(
            contents, generation_config, stream
        )
    )

    # テスト対象関数の実行(pdfファイル、pngファイルを指定)
    result = generate_content_stream(["file1.pdf", "file2.png"], "test_user")

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
@patch("app.utils.gemini_request_stream.check_file_exists", return_value=False)
@pytest.mark.asyncio
async def test_generate_content_stream_not_found(
    mock_check_file_exists: Mock, mock_GenerativeModel: Mock, mock_env_vars: None
) -> None:
    """
    ファイルが見つからない場合のエラーハンドリングのテスト

    :param mock_check_file_exists: ファイル存在確認のモック
    :type mock_check_file_exists: Mock
    :param mock_GenerativeModel: GenerativeModelのモック
    :type mock_GenerativeModel: Mock
    :param mock_env_vars: 環境変数のモックフィクスチャ
    :type mock_env_vars: None
    """
    # フィクスチャを適用
    mock_env_vars

    # テスト対象関数の実行とエラーハンドリングの確認
    with pytest.raises(NotFound) as excinfo:
        result = generate_content_stream(["non_existent_file.pdf"], "test_user")
        async for _ in result:
            pass
    expected_error_message = "File test_user/non_existent_file.pdf does not exist in the bucket"
    assert expected_error_message in str(excinfo.value)


# 無効な引数の場合のエラーハンドリングのテスト
@patch("app.utils.gemini_request_stream.GenerativeModel", autospec=True)
@patch("app.utils.gemini_request_stream.check_file_exists", return_value=True)
@pytest.mark.asyncio
async def test_generate_content_stream_invalid_argument(
    mock_check_file_exists: Mock, mock_GenerativeModel: Mock, mock_env_vars: None
) -> None:
    """
    無効な引数の場合のエラーハンドリングのテスト

    :param mock_check_file_exists: ファイル存在確認のモック
    :type mock_check_file_exists: Mock
    :param mock_GenerativeModel: GenerativeModelのモック
    :type mock_GenerativeModel: Mock
    :param mock_env_vars: 環境変数のモックフィクスチャ
    :type mock_env_vars: None
    """
    # フィクスチャを適用
    mock_env_vars
    mock_GenerativeModel.return_value.generate_content.side_effect = InvalidArgument(
        "Invalid file format"
    )

    # テスト対象関数の実行とエラーハンドリングの確認
    with pytest.raises(InvalidArgument) as excinfo:
        result = generate_content_stream(["invalid_file.txt"], "test_user")
        async for _ in result:
            pass
    assert "Invalid file format" in str(excinfo.value)


# Google APIエラーの場合のエラーハンドリングのテスト
@patch("app.utils.gemini_request_stream.GenerativeModel", autospec=True)
@patch("app.utils.gemini_request_stream.check_file_exists", return_value=True)
@pytest.mark.asyncio
async def test_generate_content_stream_google_api_error(
    mock_check_file_exists: Mock, mock_GenerativeModel: Mock, mock_env_vars: None
) -> None:
    """
    Google APIエラーの場合のエラーハンドリングのテスト

    :param mock_check_file_exists: ファイル存在確認のモック
    :type mock_check_file_exists: Mock
    :param mock_GenerativeModel: GenerativeModelのモック
    :type mock_GenerativeModel: Mock
    :param mock_env_vars: 環境変数のモックフィクスチャ
    :type mock_env_vars: None
    """
    # フィクスチャを適用
    mock_env_vars
    mock_GenerativeModel.return_value.generate_content.side_effect = GoogleAPIError(
        "Google API error"
    )

    # テスト対象関数の実行とエラーハンドリングの確認
    with pytest.raises(GoogleAPIError) as excinfo:
        result = generate_content_stream(["file1.pdf"], "test_user")
        async for _ in result:
            pass
    assert "Google API error" in str(excinfo.value)


# その他の予期しないエラーの場合のエラーハンドリングのテスト
@patch("app.utils.gemini_request_stream.GenerativeModel", autospec=True)
@patch("app.utils.gemini_request_stream.check_file_exists", return_value=True)
@pytest.mark.asyncio
async def test_generate_content_stream_unexpected_error(
    mock_check_file_exists: Mock, mock_GenerativeModel: Mock, mock_env_vars: None
) -> None:
    """
    その他の予期しないエラーの場合のエラーハンドリングのテスト

    :param mock_check_file_exists: ファイル存在確認のモック
    :type mock_check_file_exists: Mock
    :param mock_GenerativeModel: GenerativeModelのモック
    :type mock_GenerativeModel: Mock
    :param mock_env_vars: 環境変数のモックフィクスチャ
    :type mock_env_vars: None
    """
    # フィクスチャを適用
    mock_env_vars
    mock_GenerativeModel.return_value.generate_content.side_effect = Exception("Unexpected error")

    # テスト対象関数の実行とエラーハンドリングの確認
    with pytest.raises(Exception) as excinfo:
        result = generate_content_stream(["file1.pdf"], "test_user")
        async for _ in result:
            pass
    assert "Unexpected error" in str(excinfo.value)


# エラーハンドリングのテスト（モデル属性エラー）
@patch("app.utils.gemini_request_stream.GenerativeModel", autospec=True)
@patch("app.utils.gemini_request_stream.check_file_exists", return_value=True)
@pytest.mark.asyncio
async def test_generate_content_stream_attribute_error(
    mock_check_file_exists: Mock, mock_GenerativeModel: Mock, mock_env_vars: None
) -> None:
    """
    エラーハンドリングのテスト（モデル属性エラー）

    :param mock_check_file_exists: ファイル存在確認のモック
    :type mock_check_file_exists: Mock
    :param mock_GenerativeModel: GenerativeModelのモック
    :type mock_GenerativeModel: Mock
    :param mock_env_vars: 環境変数のモックフィクスチャ
    :type mock_env_vars: None
    """
    # フィクスチャを適用
    mock_env_vars
    mock_GenerativeModel.return_value.generate_content.side_effect = AttributeError(
        "Model attribute error"
    )

    # テスト対象関数の実行とエラーハンドリングの確認
    with pytest.raises(AttributeError) as excinfo:
        result = generate_content_stream(["file1.pdf", "file2.png"], "test_user")
        async for _ in result:
            pass
    assert "Model attribute error" in str(excinfo.value)


# エラーハンドリングのテスト（タイプエラー）
@patch("app.utils.gemini_request_stream.GenerativeModel", autospec=True)
@patch("app.utils.gemini_request_stream.check_file_exists", return_value=True)
@pytest.mark.asyncio
async def test_generate_content_stream_type_error(
    mock_check_file_exists: Mock, mock_GenerativeModel: Mock, mock_env_vars: None
) -> None:
    """
    エラーハンドリングのテスト（タイプエラー）

    :param mock_check_file_exists: ファイル存在確認のモック
    :type mock_check_file_exists: Mock
    :param mock_GenerativeModel: GenerativeModelのモック
    :type mock_GenerativeModel: Mock
    :param mock_env_vars: 環境変数のモックフィクスチャ
    :type mock_env_vars: None
    """
    # フィクスチャを適用
    mock_env_vars
    mock_GenerativeModel.return_value.generate_content.side_effect = TypeError(
        "Type error in model generation"
    )

    # テスト対象関数の実行とエラーハンドリングの確認
    with pytest.raises(TypeError) as excinfo:
        result = generate_content_stream(["file1.pdf", "file2.png"], "test_user")
        async for _ in result:
            pass
    assert "Type error in model generation" in str(excinfo.value)
