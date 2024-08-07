import asyncio
import logging
import os
import sys

import streamlit as st
from dotenv import load_dotenv

# プロジェクトルートのパスを取得
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# プロジェクトルートをPythonパスに追加
if project_root not in sys.path:
    sys.path.insert(0, project_root)

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


def show_output_page() -> None:
    """
    AIノートページを表示する関数。

    - ヘッダーを表示し、選択されたファイルを表示する。
    - 選択されたファイルがある場合、AIノートを生成し、セッション状態に保存する。

    :return: None
    """
    st.header("AIノート", divider="blue")

    if (
        "selected_files_note" in st.session_state
        and st.session_state.selected_files_note
    ):
        note_name = st.session_state["note_name"]
        st.subheader(f"Note Title: {note_name}")
        st.write("選択されたファイル:")
        st.text(st.session_state.selected_files_note)
        selected_files = st.session_state.get("selected_files_note", [])

        if selected_files:
            with st.spinner("処理中です。お待ちください..."):
                study_ai_note = create_study_ai_note(
                    selected_files, BACKEND_DEV_API_URL
                )
            st.session_state.study_ai_note = study_ai_note
            st.success("処理が完了しました")
            # st.session_state.page = "pages/quill_sample.py"  # ページを指定
            # st.switch_page("pages/quill_sample.py")  # ページに遷移
    else:
        st.write("ファイルが選択されていません")


# キャッシュを使用して、選択されたファイルからAIノートを生成する関数
# Streamlitのキャッシュは関数のインプットとアウトアップをkeyとvalueとして保存するので
# 全く同じインプットの関数があるとキャッシュが競合してしまうので、注意が必要。
# ここではエンドポイントのURLをインプットに追加することで競合を避けた
@st.cache_resource(show_spinner=False)
def create_study_ai_note(selected_files: list, BACKEND_DEV_API_URL: str) -> str | None:
    """
    選択されたファイルからAIノートを生成する関数。

    :param selected_files: AIノートを生成するための選択されたファイルのリスト
    :type selected_files: list
    :return: 生成されたAIノートの文字列、エラー時はNone
    :rtype: str | None
    """

    # ユーティリティ関数のインポート
    from app.utils.output import create_pdf_to_markdown_summary

    try:
        study_ai_note = asyncio.run(
            create_pdf_to_markdown_summary(selected_files, BACKEND_DEV_API_URL)
        )
        return study_ai_note
    except Exception as e:
        logging.error(f"AIノートの生成中にエラーが発生しました: {e}")
        st.error(f"AIノートの生成中にエラーが発生しました: {e}")
        return None


if __name__ == "__main__":
    from app.utils.sidebar import show_sidebar

    show_sidebar()
    show_output_page()
