import asyncio
import logging
import os

import streamlit as st
from dotenv import load_dotenv

# ユーティリティ関数のインポート
# Streemlitの仕様なのか、以下の相対パスでインポートする必要がある
# pytestでテストする際は、エラーが発生する可能性があるため、注意が必要
from utils.output import create_pdf_to_markdown_summary

# 環境変数を読み込む
load_dotenv()

# ログの設定
logging.basicConfig(level=logging.INFO)

# バックエンドAPIのURL
BACKEND_HOST = os.getenv("BACKEND_HOST")
BACKEND_DEV_API_URL = f"{BACKEND_HOST}/outputs/request_stream"

# セッション状態の初期化
if "study_ai_note" not in st.session_state:
    st.session_state.study_ai_note = ""


# AIノートページの処理
def show_output_page() -> None:
    st.header("AIノートページ", divider="rainbow")
    if "selected_files" not in st.session_state:
        st.session_state.selected_files = []
    else:
        note_name = st.session_state["note_name"]
        st.subheader(f"Note Title: {note_name}")
        st.write("選択されたファイル:")
        st.text(st.session_state.selected_files)
        selected_files = st.session_state.get("selected_files", [])

        if selected_files:
            try:
                with st.spinner("処理中です。お待ちください..."):
                    study_ai_note = create_study_ai_note(selected_files)
                st.session_state.study_ai_note = study_ai_note
                st.success("処理が完了しました")
                st.session_state.page = "pages/quill_sample.py"  # ページを指定
                st.switch_page("pages/quill_sample.py")  # ページに遷移
            except Exception as e:
                logging.error(f"問題が発生しました: {e}")
                st.error(f"エラーが発生しました: {e}")


@st.cache_resource(show_spinner=False)
def create_study_ai_note(selected_files: list) -> str:
    study_ai_note = asyncio.run(create_pdf_to_markdown_summary(selected_files))
    return study_ai_note


if __name__ == "__main__":
    show_output_page()
