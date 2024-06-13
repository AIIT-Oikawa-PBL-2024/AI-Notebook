import pytest
from unittest.mock import patch, Mock
from app.utils.gemini_request import generate_content
from pytest import MonkeyPatch
from google.api_core.exceptions import GoogleAPIError, InvalidArgument, NotFound


# 環境変数を設定するフィクスチャ
@pytest.fixture
def mock_env_vars(monkeypatch: MonkeyPatch) -> None:
    # 環境変数を設定
    monkeypatch.setenv("PROJECT_ID", "your_project_id")
    monkeypatch.setenv("REGION", "your_region")


# テストデータ
MODEL_NAME = "gemini-1.5-pro-001"
GENERATION_CONFIG = {
    "temperature": 0.1,
    "max_output_tokens": 8192,
}


# GenerativeModelクラスをモック
@patch("app.utils.gemini_request.GenerativeModel", autospec=True)
@pytest.mark.asyncio
async def test_generate_content(
    mock_GenerativeModel: Mock, mock_env_vars: None
) -> None:
    # フィクスチャを適用
    mock_env_vars

    # モックの設定
    mock_model = mock_GenerativeModel.return_value
    mock_response = mock_model.generate_content.return_value
    mock_response.text = "モックのレスポンステキスト"

    # テストデータ
    files = ["1_ソフトウェア工学の誕生.pdf", "5_アジャイルⅡ.pdf"]

    # テスト対象関数の実行
    result = await generate_content(files)

    # アサーション（検証）
    mock_GenerativeModel.assert_called_once_with(model_name=MODEL_NAME)
    mock_model.generate_content.assert_called_once()
    assert result == "モックのレスポンステキスト"


# エラーハンドリングのテスト（ファイルが見つからない場合）
@patch("app.utils.gemini_request.GenerativeModel", autospec=True)
@pytest.mark.asyncio
async def test_generate_content_file_not_found(
    mock_GenerativeModel: Mock, mock_env_vars: None
) -> None:
    # フィクスチャを適用
    mock_env_vars

    # テストデータ
    files = ["non_existent_file.pdf"]

    # モックの設定
    mock_model = mock_GenerativeModel.return_value
    mock_model.generate_content.side_effect = NotFound("File not found")

    # テスト対象関数の実行とエラーハンドリングの確認
    with pytest.raises(NotFound) as excinfo:
        await generate_content(files)

    # アサーション（検証）
    assert str(excinfo.value) == "404 File not found"


# エラーハンドリングのテスト（無効な引数）
@patch("app.utils.gemini_request.GenerativeModel", autospec=True)
@pytest.mark.asyncio
async def test_generate_content_invalid_argument(
    mock_GenerativeModel: Mock, mock_env_vars: None
) -> None:
    # フィクスチャを適用
    mock_env_vars

    # テストデータ
    files = ["invalid_format.txt"]

    # モックの設定
    mock_model = mock_GenerativeModel.return_value
    mock_model.generate_content.side_effect = InvalidArgument("Invalid file format")

    # テスト対象関数の実行とエラーハンドリングの確認
    with pytest.raises(InvalidArgument) as excinfo:
        await generate_content(files)

    # アサーション（検証）
    assert str(excinfo.value) == "400 Invalid file format"


# エラーハンドリングのテスト（Google APIエラー）
@patch("app.utils.gemini_request.GenerativeModel", autospec=True)
@pytest.mark.asyncio
async def test_generate_content_google_api_error(
    mock_GenerativeModel: Mock, mock_env_vars: None
) -> None:
    # フィクスチャを適用
    mock_env_vars

    # テストデータ
    files = ["1_ソフトウェア工学の誕生.pdf", "5_アジャイルⅡ.pdf"]

    # モックの設定
    mock_model = mock_GenerativeModel.return_value
    mock_model.generate_content.side_effect = GoogleAPIError("Google API error")

    # テスト対象関数の実行とエラーハンドリングの確認
    with pytest.raises(GoogleAPIError) as excinfo:
        await generate_content(files)

    # アサーション（検証）
    assert str(excinfo.value) == "Google API error"


# エラーハンドリングのテスト（その他の予期しないエラー）
@patch("app.utils.gemini_request.GenerativeModel", autospec=True)
@pytest.mark.asyncio
async def test_generate_content_unexpected_error(
    mock_GenerativeModel: Mock, mock_env_vars: None
) -> None:
    # フィクスチャを適用
    mock_env_vars

    # テストデータ
    files = ["1_ソフトウェア工学の誕生.pdf", "5_アジャイルⅡ.pdf"]

    # モックの設定
    mock_model = mock_GenerativeModel.return_value
    mock_model.generate_content.side_effect = Exception("Unexpected error")

    # テスト対象関数の実行とエラーハンドリングの確認
    with pytest.raises(Exception) as excinfo:
        await generate_content(files)

    # アサーション（検証）
    assert str(excinfo.value) == "Unexpected error"


# エラーハンドリングのテスト（モデル属性エラー）
@patch("app.utils.gemini_request.GenerativeModel", autospec=True)
@pytest.mark.asyncio
async def test_generate_content_attribute_error(
    mock_GenerativeModel: Mock, mock_env_vars: None
) -> None:
    # フィクスチャを適用
    mock_env_vars

    # テストデータ
    files = ["1_ソフトウェア工学の誕生.pdf", "5_アジャイルⅡ.pdf"]

    # モックの設定
    mock_model = mock_GenerativeModel.return_value
    mock_model.generate_content.side_effect = AttributeError("Model attribute error")

    # テスト対象関数の実行とエラーハンドリングの確認
    with pytest.raises(AttributeError) as excinfo:
        await generate_content(files)

    # アサーション（検証）
    assert str(excinfo.value) == "Model attribute error"


# エラーハンドリングのテスト（タイプエラー）
@patch("app.utils.gemini_request.GenerativeModel", autospec=True)
@pytest.mark.asyncio
async def test_generate_content_type_error(
    mock_GenerativeModel: Mock, mock_env_vars: None
) -> None:
    # フィクスチャを適用
    mock_env_vars

    # テストデータ
    files = ["1_ソフトウェア工学の誕生.pdf", "5_アジャイルⅡ.pdf"]

    # モックの設定
    mock_model = mock_GenerativeModel.return_value
    mock_model.generate_content.side_effect = TypeError(
        "Type error in model generation"
    )

    # テスト対象関数の実行とエラーハンドリングの確認
    with pytest.raises(TypeError) as excinfo:
        await generate_content(files)

    # アサーション（検証）
    assert str(excinfo.value) == "Type error in model generation"
