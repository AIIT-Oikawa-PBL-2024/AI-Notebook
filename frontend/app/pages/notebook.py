import asyncio
import logging
import os

import streamlit as st
from dotenv import load_dotenv

# ユーティリティ関数のインポート
from utils.output import create_pdf_to_markdown_summary

# 環境変数を読み込む
load_dotenv()

# ログの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# バックエンドAPIのURL
BACKEND_HOST = os.getenv("BACKEND_HOST")
BACKEND_API_URL = f"{BACKEND_HOST}/notes/"

# セッション状態の初期化
if "note_title" not in st.session_state:
    st.session_state.note_title = ""
if "markdown_text" not in st.session_state:
    st.session_state.markdown_text = ""
if "show_preview" not in st.session_state:
    st.session_state.show_preview = False
if "current_note_id" not in st.session_state:
    st.session_state.current_note_id = None
if "notes_df" not in st.session_state:
    st.session_state.notes_df = None
if "pages" not in st.session_state:
    st.session_state.pages = []
if "selected_files" not in st.session_state:
    st.session_state.selected_files = []
if "processing_summary" not in st.session_state:
    st.session_state.processing_summary = False
if "summary_result" not in st.session_state:
    st.session_state.summary_result = ""

# 既存の関数（preprocess_markdown, validate_title, create_new_note, get_notes_and_pages, save_note, create_and_post_new_note）はそのまま維持


async def process_summary() -> None:
    try:
        result = await create_pdf_to_markdown_summary(st.session_state.selected_files)
        st.session_state.summary_result = result
        st.session_state.processing_summary = False
    except Exception as e:
        logging.error(f"問題が発生しました: {e}")
        st.session_state.summary_result = f"エラーが発生しました: {e}"
        st.session_state.processing_summary = False


def display_note_content() -> None:
    if st.session_state.notes_df is None or st.session_state.pages == []:
        get_notes_and_pages()

    # 新規ノート作成ボタン
    if st.button("新規ノート作成"):
        create_and_post_new_note()

    note_title: str = st.text_input(
        "ノートのタイトル", value=st.session_state.note_title, key="note_title"
    )

    is_valid, error_message = validate_title(note_title)
    if not is_valid:
        st.error(error_message)

    st.write(f"タイトル文字数: {len(note_title)}/200")

    st.subheader("ノート")

    col1, col2, _ = st.columns([1, 1, 2])
    with col1:
        edit_button = st.button("テキスト編集", use_container_width=True)
    with col2:
        preview_button = st.button("プレビュー表示", use_container_width=True)

    if preview_button:
        st.session_state.show_preview = True
    if edit_button:
        st.session_state.show_preview = False

    if st.session_state.processing_summary:
        with st.spinner("処理中です。お待ちください..."):
            asyncio.run(process_summary())

    if st.session_state.summary_result:
        st.session_state.markdown_text = st.session_state.summary_result
        st.session_state.summary_result = ""  # 結果を表示したらクリア

    if not st.session_state.show_preview:
        markdown_text: str = st.text_area(
            "テキストをここに入力してください",
            value=st.session_state.markdown_text,
            height=500,
            key="markdown_input",
            max_chars=15000,
        )
        st.session_state.markdown_text = markdown_text

        st.write(f"本文文字数: {len(markdown_text)}/15000")
    else:
        processed_text: str = preprocess_markdown(st.session_state.markdown_text)
        st.markdown(processed_text)

    _, _, _, save_col = st.columns([1, 1, 1, 1])
    with save_col:
        if st.button("保存", use_container_width=True):
            if is_valid:
                save_note(note_title, st.session_state.markdown_text)
            else:
                st.error("タイトルが無効です。保存できません。")


def main() -> None:
    st.set_page_config(layout="wide")

    st.title("AIサポート学習帳")

    # サイドバーにノート選択を配置
    with st.sidebar:
        if (
            st.session_state.notes_df is not None
            and not st.session_state.notes_df.empty
        ):
            note_titles = st.session_state.notes_df["title"].tolist()
            note_titles.insert(0, "新規ノート")
            selected_note = st.selectbox("ノートを選択", note_titles)

            if selected_note != "新規ノート":
                selected_note_data = st.session_state.notes_df[
                    st.session_state.notes_df["title"] == selected_note
                ].iloc[0]
                st.session_state.current_note_id = selected_note_data["id"]
                st.session_state.note_title = selected_note_data["title"]
                st.session_state.markdown_text = selected_note_data["content"]
            else:
                create_new_note()
        else:
            st.warning("ノートが見つかりません。新しいノートを作成してください。")

    display_note_content()


if __name__ == "__main__":
    main()
