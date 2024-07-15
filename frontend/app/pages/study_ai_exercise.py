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
BACKEND_DEV_API_URL = f"{BACKEND_HOST}/exercises/request_stream"

# セッション状態の初期化
if "study_ai_exercise" not in st.session_state:
    st.session_state.study_ai_exercise = ""


def show_output_page() -> None:
    """
    AI練習問題を表示する関数。

    - ヘッダーを表示し、選択されたファイルを表示する。
    - 選択されたファイルがある場合、AI練習問題を生成し、セッション状態に保存する。

    :return: None
    """
    st.header("AI練習問題", divider="blue")

    if (
        "selected_files_exercise" in st.session_state
        and st.session_state.selected_files_exercise
    ):
        exercise_name = st.session_state["exercise_name"]
        st.subheader(f"Exercise Title: {exercise_name}")
        st.write("選択されたファイル:")
        st.text(st.session_state.selected_files_exercise)
        selected_files = st.session_state.get("selected_files_exercise", [])

        if selected_files:
            with st.spinner("処理中です。お待ちください..."):
                study_ai_exercise = create_study_ai_exercise(
                    selected_files, BACKEND_DEV_API_URL
                )
            st.session_state.study_ai_exercise = study_ai_exercise
            st.success("処理が完了しました")
    else:
        st.write("ファイルが選択されていません")


# キャッシュを使用して、選択されたファイルからAI練習問題を生成する関数
# Streamlitのキャッシュは関数のインプットとアウトアップをkeyとvalueとして保存するので
# 全く同じインプットの関数があるとキャッシュが競合してしまうので、注意が必要
# ここではエンドポイントのURLをインプットに追加することで競合を避けた
@st.cache_resource(show_spinner=False)
def create_study_ai_exercise(
    selected_files: list, BACKEND_DEV_API_URL: str
) -> str | None:
    """
    選択されたファイルからAI練習問題を生成する関数。

    :param selected_files: AI練習問題を生成するための選択されたファイルのリスト
    :type selected_files: list
    :return: 生成されたAI練習問題の文字列、エラー時はNone
    :rtype: str | None
    """

    # ユーティリティ関数のインポート
    from app.utils.output import create_pdf_to_markdown_summary

    try:
        study_ai_exercise = asyncio.run(
            create_pdf_to_markdown_summary(selected_files, BACKEND_DEV_API_URL)
        )
        return study_ai_exercise
    except Exception as e:
        logging.error(f"AI練習問題の生成中にエラーが発生しました: {e}")
        st.error(f"AI練習問題の生成中にエラーが発生しました: {e}")
        return None


if __name__ == "__main__":
    from app.utils.sidebar import show_sidebar

    show_sidebar()
    show_output_page()
