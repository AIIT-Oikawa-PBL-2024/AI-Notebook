import asyncio
import logging
import os
import sys
from datetime import datetime

import httpx
import json
import pandas as pd
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
logger = logging.getLogger(__name__)

# バックエンドAPIのURL
BACKEND_HOST = os.getenv("BACKEND_HOST")
BACKEND_DEV_API_URL = f"{BACKEND_HOST}/files/"
BACKEND_DELETE_API_URL = f"{BACKEND_HOST}/files/delete_files"

# セッション状態の初期化
if "title_name" not in st.session_state:
    st.session_state.title_name = ""
if "exercise_name" not in st.session_state:
    st.session_state.exercise_name = ""
if "note_name" not in st.session_state:
    st.session_state.note_name = ""
if "df" not in st.session_state:
    st.session_state.df = None
if "df_updated" not in st.session_state:
    st.session_state.df_updated = False
if "selected_files" not in st.session_state:
    st.session_state.selected_files = []


# 時刻フォーマットを変換する関数
def time_format(jst_str: str) -> str:
    """
    JST形式の文字列を指定のフォーマットに変換する。

    :param jst_str: JST形式の日時文字列
    :type jst_str: str
    :return: 変換後の日時文字列
    :rtype: str
    """
    jst_time = datetime.fromisoformat(jst_str.replace("Z", "+00:00"))
    return jst_time.strftime("%Y-%m-%d %H:%M:%S")


# 非同期でファイル一覧を取得する関数
async def get_files_list() -> list[str]:
    """
    バックエンドAPIからファイル一覧を非同期で取得する。

    :return: ファイル一覧
    :rtype: list[str]
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                BACKEND_DEV_API_URL, timeout=100, headers={"accept": "application/json"}
            )
            response.raise_for_status()
            files = response.json()
            return files
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP Status Error: {e}")
        st.error("ファイル一覧の取得に失敗しました(HTTP Status Error)")
    except httpx.RequestError as e:
        logger.error(f"Request Error: {e}")
        st.error("ファイル一覧の取得に失敗しました(Request Error)")
    except Exception as e:
        logger.error(f"Error: {e}")
        st.error("ファイル一覧の取得に失敗しました(Error)")
    return []


# 非同期でファイル一覧を作成して表示する関数
async def show_files_list_df() -> None:
    """
    ファイル一覧をデータフレーム形式で表示する。

    :return: None
    """
    if st.session_state.df is None:
        files = await get_files_list()
        file_df = pd.DataFrame(files)
        # id列, user_id列を削除
        file_df.drop(columns=["id", "user_id"], inplace=True)
        # created_at列の時刻フォーマットを変換
        file_df["created_at"] = file_df["created_at"].apply(time_format)
        # 新しい boolean 型の列を一番左に追加
        file_df.insert(0, "select", False)
        st.session_state.df = file_df
    st.data_editor(
        st.session_state.df,
        key="changes",
        on_change=update,
        hide_index=True,
        disabled=("file_name", "file_size", "created_at"),
        column_config={
            "file_name": st.column_config.TextColumn(
                "file_name",
            )
        },
        use_container_width=True,
    )


# データを更新する関数
def update() -> None:
    """
    データフレームの変更をセッション状態に反映する。

    :return: None
    """
    if "changes" in st.session_state:
        changes = st.session_state.changes.get("edited_rows", {})
        for idx, change in changes.items():
            for label, value in change.items():
                st.session_state.df.at[idx, label] = value
        st.session_state.df_updated = True


# 選択されたファイル名をリスト形式で取得する関数
def get_selected_files() -> list[str]:
    """
    選択されたファイル名をリスト形式で取得する。

    :return: 選択されたファイル名のリスト
    :rtype: list[str]
    """
    if st.session_state.df is not None:
        selected_files = st.session_state.df[st.session_state.df["select"]][
            "file_name"
        ].tolist()
        return selected_files
    return []

# ファイルを削除する非同期関数 -> 現在修正中
async def delete_selected_files(files: list[str]) -> None:
    """
    選択されたファイルを削除する。

    :param files: 削除するファイルのリスト
    :type files: list[str]
    :return: None
    """
    try:
        user_id = 1  # ユーザーIDを固定値（1）で設定
        request_data = {
            "files": files,
            "user_id": user_id
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                BACKEND_DELETE_API_URL,
                json=request_data  # httpxはjsonパラメータを使用できます
            )
            response.raise_for_status()
            result = response.json()
            if result.get("success", False):
                st.success("選択したファイルを削除しました。")
                st.session_state.df = None  # データフレームをリセット
                if result.get("failed_files"):
                    st.warning(f"一部のファイルの削除に失敗しました: {', '.join(result['failed_files'])}")
            else:
                st.error("ファイルの削除に失敗しました。")
                if "detail" in result:
                    st.error(f"エラー詳細: {result['detail']}")
    except httpx.HTTPStatusError as e:
        st.error(f"HTTP Status Error: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        st.error(f"Request Error: {e}")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# ファイル選択ページの処理
async def show_select_files_page() -> None:
    """
    ファイル選択ページを表示する。

    :return: None
    """
    # st.set_page_config(layout="wide")
    st.session_state.page = "pages/select_files.py"
    st.header("AIノートを作成", divider="blue")

    # ボタンの配置
    col1, col2, col3, _ = st.columns([1.5, 1, 1.5, 1])
    with col1:
        get_files_button = st.button("ファイル一覧を取得", use_container_width=True)
    with col2:
        reset_button = st.button("リセット", use_container_width=True)
    with col3:
        delete_button = st.button("選択したファイルを削除", use_container_width=True, type="secondary")

    # ボタンが押された場合の処理
    if get_files_button:
        await show_files_list_df()

    if reset_button:
        st.session_state.clear()
        st.rerun()  
    # ファイル削除ボタンが押された場合の処理を追記しております（若林）
    if delete_button:
        selected_files = get_selected_files()
        if selected_files:
            await delete_selected_files(selected_files)
            # ファイル一覧を再取得
            await show_files_list_df()
        else:
            st.warning("削除するファイルを選択してください。")

    # データフレームがセッション状態にある場合、表示
    if st.session_state.df is not None:
        if st.session_state.df_updated:
            await show_files_list_df()  # フィルター機能を含む表示関数を呼び出す
            st.session_state.df_updated = False

        # 選択されたファイルを表示
        selected_files = get_selected_files()
        if selected_files:
            st.write(":blue-background[選択されたファイル]")
            st.text(selected_files)
            st.divider()

            # タイトルを入力
            st.write(":blue-background[タイトル]")
            st.text_input(
                "AIで作成するノートや練習問題のタイトルを100文字以内で入力してEnterキーを押して下さい",
                key="title_input",
                value=st.session_state.title_name,
                on_change=update_title_name,
                max_chars=100,
            )

            # 現在のタイトルを表示
            st.write(f"Title:  {st.session_state.title_name}")

            # AIノート作成ボタン
            if selected_files and st.session_state.title_name:
                st.divider()
                if st.button(
                    "AIノートを作成", use_container_width=True, type="primary"
                ):
                    st.session_state.note_name = st.session_state.title_name
                    st.session_state.selected_files = (
                        selected_files  # 選択されたファイルをセッション状態に保存
                    )
                    st.session_state.page = "pages/study_ai_note.py"  # ページを指定
                    st.switch_page("pages/study_ai_note.py")  # ページに遷移

            # AI練習問題作成ボタン
            if selected_files and st.session_state.title_name:
                st.divider()
                if st.button(
                    "AI練習問題を作成", use_container_width=True, type="primary"
                ):
                    st.session_state.exercise_name = st.session_state.title_name
                    st.session_state.selected_files = (
                        selected_files  # 選択されたファイルをセッション状態に保存
                    )
                    st.session_state.page = "pages/study_ai_exercise.py"  # ページを指定
                    st.switch_page("pages/study_ai_exercise.py")  # ページに遷移


# タイトル名を更新する数
def update_title_name() -> None:
    """
    タイトル名をセッション状態に反映する。

    :return: None
    """
    st.session_state.title_name = st.session_state.title_input


# ファイル選択ページの処理を実行
if __name__ == "__main__":
    from app.utils.sidebar import show_sidebar

    show_sidebar()
    asyncio.run(show_select_files_page())