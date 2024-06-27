import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone

import httpx
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

# ログの設定
logging.basicConfig(level=logging.INFO)

# バックエンドAPIのURL
BACKEND_HOST = os.getenv("BACKEND_HOST")
BACKEND_DEV_API_URL = f"{BACKEND_HOST}/files/"

# 日本のタイムゾーンを設定
JST = timezone(timedelta(hours=9))

# セッション状態の初期化
if "note_name" not in st.session_state:
    st.session_state.note_name = ""
if "df" not in st.session_state:
    st.session_state.df = None
if "df_updated" not in st.session_state:
    st.session_state.df_updated = False
if "selected_files" not in st.session_state:
    st.session_state.selected_files = []


# UTCをJSTに変換する関数
def utc_to_jst(utc_str: str) -> str:
    utc_time = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
    jst_time = utc_time.astimezone(JST)
    return jst_time.strftime("%Y-%m-%d %H:%M:%S")


# 非同期でファイル一覧を取得する関数
async def get_files_list() -> list[str]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            BACKEND_DEV_API_URL, timeout=100, headers={"accept": "application/json"}
        )
        response.raise_for_status()
        files = response.json()
        return files


# 非同期でファイル一覧を作成して表示する関数
async def show_files_list_df() -> None:
    if st.session_state.df is None:
        files = await get_files_list()
        file_df = pd.DataFrame(files)
        # created_at列をJSTに変換
        file_df["created_at"] = file_df["created_at"].apply(utc_to_jst)
        # 新しい boolean 型の列を一番左に追加
        file_df.insert(0, "select", False)
        st.session_state.df = file_df
    st.data_editor(
        st.session_state.df, key="changes", on_change=update, hide_index=True
    )


# データを更新する関数
def update() -> None:
    if "changes" in st.session_state:
        changes = st.session_state.changes.get("edited_rows", {})
        for idx, change in changes.items():
            for label, value in change.items():
                st.session_state.df.at[idx, label] = value
        st.session_state.df_updated = True


# 選択されたファイル名をリスト形式で取得する関数
def get_selected_files() -> list[str]:
    if st.session_state.df is not None:
        selected_files = st.session_state.df[st.session_state.df["select"]][
            "file_name"
        ].tolist()
        return selected_files
    return []


# ファイル選択ページの処理
async def show_select_files_page() -> None:
    st.session_state.page = "pages/select_files.py"
    st.header("ファイルリスト表示", divider="rainbow")
    if st.button("ファイル一覧を取得"):
        await show_files_list_df()

    # データフレームがセッション状態にある場合、表示
    if st.session_state.df is not None:
        if st.session_state.df_updated:
            await show_files_list_df()  # フィルター機能を含む表示関数を呼び出す
            st.session_state.df_updated = False

        # 選択されたファイルを表示
        selected_files = get_selected_files()
        if selected_files:
            st.write("選択されたファイル:")
            st.text(selected_files)

            # ノート名を入力
            st.text_input(
                "ノートのタイトルを入力してEnterキーを押して下さい",
                key="note_input",
                value=st.session_state.note_name,
                on_change=update_note_name,
            )

            # 現在のノートタイトルを表示
            st.write(f"Note Title:  {st.session_state.note_name}")
            st.divider()

        # 学習帳作成ボタン
        if st.button("学習帳を作成"):
            st.session_state.selected_files = (
                selected_files  # 選択されたファイルをセッション状態に保存
            )
            st.session_state.page = "pages/study_ai_note.py"  # ページを指定
            st.switch_page("pages/study_ai_note.py")  # ページに遷移

    # リセットボタン
    st.divider()
    if st.button("リセット"):
        st.session_state.clear()
        st.rerun()


# note_nameを更新する関数
def update_note_name() -> None:
    st.session_state.note_name = st.session_state.note_input


# ファイル選択ページの処理を実行
if __name__ == "__main__":
    asyncio.run(show_select_files_page())