import pytest
from unittest.mock import patch, Mock
from app.utils.gemini_request import generate_content
from pytest import MonkeyPatch


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
    "response_mime_type": "application/json",
}


# GenerativeModelクラスをモック
@patch("app.utils.gemini_request.GenerativeModel", autospec=True)
def test_generate_content(mock_GenerativeModel: Mock, mock_env_vars: None) -> None:
    # フィクスチャを適用
    mock_env_vars

    # モックの設定
    mock_model = mock_GenerativeModel.return_value
    mock_response = mock_model.generate_content.return_value
    mock_response.text = {"response": "mocked response text"}

    # テストデータ
    files = ["1_ソフトウェア工学の誕生.pdf", "5_アジャイルⅡ.pdf"]

    # テスト対象関数の実行
    result = generate_content(files)

    # アサーション（検証）
    mock_GenerativeModel.assert_called_once_with(model_name=MODEL_NAME)
    mock_model.generate_content.assert_called_once()
    assert result == {"response": "mocked response text"}
