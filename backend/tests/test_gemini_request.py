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


# GenerativeModelクラスをモック
@patch("app.utils.gemini_request.GenerativeModel", autospec=True)
def test_generate_content(mock_GenerativeModel: Mock, mock_env_vars: None) -> None:
    # フィクスチャを適用
    mock_env_vars

    # モックの設定
    mock_model = mock_GenerativeModel.return_value
    mock_response = mock_model.generate_content.return_value
    mock_response.text = "mocked response text"

    # テストデータ
    pdf_file_uri = "gs://ai-notebook-test001/5_アジャイルⅡ.pdf"
    prompt = """
    あなたは、わかりやすく丁寧に教えることで評判の大学教授です。
    ソフトウェア工学についてのスライド資料と解説です。
    この資料と解説に基づいて、わかりやすく、親しみやすい解説がついていて、誰もが読みたくなるような整理ノートを作成して下さい。
    ビジュアル的にもわかりやすくするため、マークダウンで文字の大きさ、強調表示などのスタイルを作成して、スライド資料の図を複数挿入できるようにスライドのページと配置を指定してください。
    また、コラムや用語解説を複数つけて、興味を持てるようにしてください。
    最後に選択式と穴埋め式の練習問題を付けてください。
    問題の解答は、最後に別枠で記載してください。
    出力のファイル形式は、マークダウンのファイルで出力してください。
    """

    # テスト対象関数の実行
    result = generate_content(pdf_file_uri, prompt)

    # アサーション（検証）
    mock_GenerativeModel.assert_called_once_with(model_name="gemini-1.5-pro-001")
    mock_model.generate_content.assert_called_once()
    assert result == "mocked response text"
