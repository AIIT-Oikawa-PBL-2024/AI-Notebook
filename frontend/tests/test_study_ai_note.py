import os
import pytest
from unittest.mock import patch, MagicMock
import streamlit as st
from app.pages.study_ai_note import create_study_ai_note, show_output_page
from typing import Generator


# テスト用のフィクスチャ
@pytest.fixture
def mock_session_state() -> Generator:
    st.session_state.selected_files_note = ["file1.pdf", "file2.pdf"]
    st.session_state.note_name = "Test Note"
    yield
    st.session_state.clear()


# バックエンドAPIのURL
BACKEND_HOST = os.getenv("BACKEND_HOST")
BACKEND_DEV_API_URL = f"{BACKEND_HOST}/outputs/request_stream"


# AIノートの生成が成功する場合のテスト
@patch("app.utils.output.create_pdf_to_markdown_summary")
def test_create_study_ai_note_success(
    mock_create_pdf_to_markdown_summary: MagicMock, mock_session_state: Generator
) -> None:
    mock_create_pdf_to_markdown_summary.return_value = "Mocked AI Note"
    result = create_study_ai_note(
        st.session_state.selected_files_note, BACKEND_DEV_API_URL
    )
    assert result == "Mocked AI Note"
    mock_create_pdf_to_markdown_summary.assert_called_once_with(
        st.session_state.selected_files_note, BACKEND_DEV_API_URL
    )


# AIノートの生成が失敗する場合のテスト
# @patch("app.utils.output.create_pdf_to_markdown_summary")
# @patch("app.pages.study_ai_note.logging")
# @patch("streamlit.error")
# def test_create_study_ai_note_exception(
#     mock_error: MagicMock,
#     mock_logging: MagicMock,
#     mock_create_pdf_to_markdown_summary: MagicMock,
#     mock_session_state: Generator,
# ) -> None:
#     mock_create_pdf_to_markdown_summary.side_effect = Exception("Test Exception")
#     result = create_study_ai_note(
#         st.session_state.selected_files_note, BACKEND_DEV_API_URL
#     )
#     assert result is None
#     mock_logging.error.assert_called_once_with(
#         "AIノートの生成中にエラーが発生しました: Test Exception"
#     )
#     mock_error.assert_called_once_with(
#         "AIノートの生成中にエラーが発生しました: Test Exception"
#     )


# ページの表示が成功する場合のテスト
@patch("app.pages.study_ai_note.create_study_ai_note")
@patch("streamlit.spinner")
@patch("streamlit.success")
@patch("streamlit.error")
@patch("streamlit.subheader")
@patch("streamlit.write")
@patch("streamlit.text")
@patch("streamlit.header")
def test_show_output_page_success(
    mock_header: MagicMock,
    mock_text: MagicMock,
    mock_write: MagicMock,
    mock_subheader: MagicMock,
    mock_error: MagicMock,
    mock_success: MagicMock,
    mock_spinner: MagicMock,
    mock_create_study_ai_note: MagicMock,
    mock_session_state: Generator,
) -> None:
    mock_create_study_ai_note.return_value = "Mocked AI Note"
    show_output_page()
    mock_header.assert_called_once_with("AIノート", divider="blue")
    mock_subheader.assert_called_once_with(f"Note Title: {st.session_state.note_name}")
    mock_write.assert_called_once_with("選択されたファイル:")
    mock_text.assert_called_once_with(st.session_state.selected_files_note)
    mock_spinner.assert_called_once_with("処理中です。お待ちください...")
    mock_create_study_ai_note.assert_called_once_with(
        st.session_state.selected_files_note, BACKEND_DEV_API_URL
    )
    mock_success.assert_called_once_with("処理が完了しました")
    mock_error.assert_not_called()
