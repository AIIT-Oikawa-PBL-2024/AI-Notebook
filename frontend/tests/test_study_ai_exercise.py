import pytest
from unittest.mock import patch, MagicMock
import streamlit as st
from app.pages.study_ai_exercise import create_study_ai_exercise, show_output_page
from typing import Generator


# テスト用のフィクスチャ
@pytest.fixture
def mock_session_state() -> Generator:
    st.session_state.selected_files = ["file1.pdf", "file2.pdf"]
    st.session_state.exercise_name = "Test Xxercise"
    yield
    st.session_state.clear()


# AI練習問題の生成が成功する場合のテスト
@patch("app.utils.output.create_pdf_to_markdown_summary")
def test_create_study_ai_exercise_success(
    mock_create_pdf_to_markdown_summary: MagicMock, mock_session_state: Generator
) -> None:
    mock_create_pdf_to_markdown_summary.return_value = "Mocked AI Exercise"
    result = create_study_ai_exercise(st.session_state.selected_files)
    assert result == "Mocked AI Exercise"
    mock_create_pdf_to_markdown_summary.assert_called_once_with(
        st.session_state.selected_files
    )


# AI練習問題の生成が失敗する場合のテスト
@patch("app.utils.output.create_pdf_to_markdown_summary")
@patch("app.pages.study_ai_exercise.logging")
@patch("streamlit.error")
def test_create_study_ai_exercise_exception(
    mock_error: MagicMock,
    mock_logging: MagicMock,
    mock_create_pdf_to_markdown_summary: MagicMock,
    mock_session_state: Generator,
) -> None:
    mock_create_pdf_to_markdown_summary.side_effect = Exception("Test Exception")
    result = create_study_ai_exercise(st.session_state.selected_files)
    assert result is None
    mock_logging.error.assert_called_once_with(
        "AI練習問題の生成中にエラーが発生しました: Test Exception"
    )
    mock_error.assert_called_once_with(
        "AI練習問題の生成中にエラーが発生しました: Test Exception"
    )


# ページの表示が成功する場合のテスト
@patch("app.pages.study_ai_exercise.create_study_ai_exercise")
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
    mock_create_study_ai_exercise: MagicMock,
    mock_session_state: Generator,
) -> None:
    mock_create_study_ai_exercise.return_value = "Mocked AI Exercise"
    show_output_page()
    mock_header.assert_called_once_with("AI練習問題", divider="blue")
    mock_subheader.assert_called_once_with(
        f"Exercise Title: {st.session_state.exercise_name}"
    )
    mock_write.assert_called_once_with("選択されたファイル:")
    mock_text.assert_called_once_with(st.session_state.selected_files)
    mock_spinner.assert_called_once_with("処理中です。お待ちください...")
    mock_create_study_ai_exercise.assert_called_once_with(
        st.session_state.selected_files
    )
    mock_success.assert_called_once_with("処理が完了しました")
    mock_error.assert_not_called()
