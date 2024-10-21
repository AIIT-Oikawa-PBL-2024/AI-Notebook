import asyncio
import logging
import os
import re
import sys
from typing import Any

import httpx
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
# プロジェクトルートのパスを取得
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# プロジェクトルートをPythonパスに追加
if project_root not in sys.path:
    sys.path.insert(0, project_root)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
st.set_page_config(layout="wide")

BACKEND_HOST = os.getenv("BACKEND_HOST")
BACKEND_API_URL = f"{BACKEND_HOST}/notes/"


def init_session_state() -> None:
    """
    セッション状態を初期化する。

    デフォルト値が設定されていない場合、各キーにデフォルト値を設定する。
    """
    default_values = {
        "note_title": "",
        "markdown_text": "",
        "show_preview": False,
        "current_note_id": None,
        "notes_df": None,
        "note_titles": [],
        "user_id": 1,
        "unsaved_changes": {},
        "last_saved_note": None,
        "selected_note": None,
        "show_new_note": False,
    }
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


def preprocess_markdown(text: str) -> str:
    """
    マークダウンテキストを前処理する。

    :param text: 前処理するマークダウンテキスト
    :type text: str
    :return: 前処理されたマークダウンテキスト
    :rtype: str
    """
    lines = text.split("\n")
    lines = [line.rstrip() + "  " for line in lines]
    text = "\n".join(lines)

    patterns = [
        (r"^(#+)([^#\s])", r"\1 \2"),
        (r"^([-*+])([^\s])", r"\1 \2"),
        (r"^(\d+\.)([^\s])", r"\1 \2"),
        (r"^(>)([^\s])", r"\1 \2"),
        (r"^(\s*[-*+])([^\s])", r"\1 \2"),
        (r"^(\s*\d+\.)([^\s])", r"\1 \2"),
    ]

    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.MULTILINE)

    return text


def validate_title(title: str) -> tuple[bool, str]:
    """
    ノートのタイトルを検証する。

    :param title: 検証するタイトル
    :type title: str
    :return: 検証結果（有効かどうか）とエラーメッセージ（ある場合）
    :rtype: tuple[bool, str]
    """
    if not title.strip():
        return False, "タイトルは必須です。"
    if len(title) > 200:
        return False, "タイトルは200文字以内で入力してください。"
    if title.isspace():
        return False, "タイトルにスペースのみの入力は無効です。"
    return True, ""


async def get_notes() -> None:
    """
    バックエンドからノート情報を取得し、セッション状態を更新する。

    非同期関数。HTTPリクエストを行い、取得したデータを処理してDataFrameに変換する。
    エラーが発生した場合はエラーメッセージを表示する。
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(BACKEND_API_URL)
            response.raise_for_status()
            notes = response.json()

        processed_notes = []
        for note in notes:
            try:
                processed_note = {
                    "id": note["id"],
                    "title": note["title"],
                    "content": note["content"],
                    "user_id": note.get("user_id", "Unknown"),
                    "created_at": note.get("created_at"),
                    "updated_at": note.get("updated_at"),
                }
                for field in ["created_at", "updated_at"]:
                    if processed_note[field]:
                        try:
                            processed_note[field] = pd.to_datetime(
                                processed_note[field]
                            ).strftime("%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            logger.warning(
                                f"Failed to parse {field} for note {note['id']}"
                            )
                processed_notes.append(processed_note)
            except KeyError as e:
                logger.warning(f"Skipping note due to missing key: {e}")

        st.session_state.notes_df = pd.DataFrame(processed_notes)
        st.session_state.note_titles = list(
            dict.fromkeys(st.session_state.notes_df["title"].tolist())
        )

    except httpx.HTTPStatusError as e:
        st.error(f"ノート情報の取得に失敗しました: {e}")
    except Exception as e:
        st.error(f"予期せぬエラーが発生しました: {e}")
        logger.error(f"Error in get_notes: {e}", exc_info=True)


def create_new_note() -> None:
    """
    新しいノートを作成するための初期化を行う。

    現在のノートIDをリセットし、タイトルと本文をクリアする。
    """
    st.session_state.current_note_id = None
    if "新規ノート" in st.session_state.unsaved_changes:
        st.session_state.note_title = st.session_state.unsaved_changes["新規ノート"][
            "title"
        ]
        st.session_state.markdown_text = st.session_state.unsaved_changes["新規ノート"][
            "content"
        ]
    else:
        st.session_state.note_title = ""
        st.session_state.markdown_text = ""
    st.session_state.show_preview = False


async def save_note(client: httpx.AsyncClient, title: str, content: str) -> None:
    """
    ノートを保存する。

    :param client: 非同期HTTPクライアント
    :type client: httpx.AsyncClient
    :param title: ノートのタイトル
    :type title: str
    :param content: ノートの本文
    :type content: str
    """
    payload = {"title": title, "content": content, "user_id": st.session_state.user_id}
    try:
        existing_note = st.session_state.notes_df[
            st.session_state.notes_df["title"] == title
        ]
        if not existing_note.empty:
            note_id = existing_note.iloc[0]["id"]
            url = f"{BACKEND_API_URL}{note_id}"
            response = await client.put(url, json=payload)
        elif st.session_state.current_note_id:
            url = f"{BACKEND_API_URL}{st.session_state.current_note_id}"
            response = await client.put(url, json=payload)
        else:
            response = await client.post(BACKEND_API_URL, json=payload)

        response.raise_for_status()

        saved_note = response.json()
        st.session_state.current_note_id = saved_note.get("id")

        if st.session_state.current_note_id:
            st.session_state.unsaved_changes.pop(
                str(st.session_state.current_note_id), None
            )
        else:
            st.session_state.unsaved_changes.pop("新規ノート", None)

        st.session_state.last_saved_note = {
            "id": st.session_state.current_note_id,
            "title": title,
        }

        st.success("ノートを保存しました。")
        await get_notes()

        st.session_state.selected_note = title
        st.session_state.show_new_note = False
        st.session_state.note_title = title

    except httpx.HTTPStatusError as e:
        error_detail = e.response.text
        st.error(f"ノートの保存に失敗しました: {e}\n詳細: {error_detail}")
    except Exception as e:
        st.error(f"予期せぬエラーが発生しました: {e}")


async def create_and_post_new_note(client: httpx.AsyncClient) -> None:
    """
    新しいノートを作成して保存する。

    :param client: 非同期HTTPクライアント
    :type client: httpx.AsyncClient
    """
    title = "新規ノート"
    content = ""
    try:
        payload = {
            "title": title,
            "content": content,
            "user_id": st.session_state.user_id,
        }
        response = await client.post(BACKEND_API_URL, json=payload)
        response.raise_for_status()
        new_note = response.json()

        st.session_state.current_note_id = new_note.get("id")
        st.session_state.note_title = new_note.get("title", title)
        st.session_state.markdown_text = new_note.get("content", content)

        st.session_state.unsaved_changes.pop("新規ノート", None)

        st.session_state.last_saved_note = {
            "id": st.session_state.current_note_id,
            "title": st.session_state.note_title,
        }

        await get_notes()

        st.sidebar.success("新しいノートを作成しました。")

    except httpx.HTTPStatusError as e:
        error_detail = e.response.text
        st.sidebar.error(f"新しいノートの作成に失敗しました: {e}\n詳細: {error_detail}")
        logger.error(f"Failed to create new note: {e}\nDetail: {error_detail}")
    except Exception as e:
        st.sidebar.error(f"予期せぬエラーが発生しました: {e}")
        logger.error(
            f"Unexpected error in create_and_post_new_note: {e}", exc_info=True
        )


def update_unsaved_changes(title: str, content: str) -> None:
    """
    未保存の変更を更新する。

    :param title: ノートのタイトル
    :type title: str
    :param content: ノートの本文
    :type content: str
    """
    key = (
        str(st.session_state.current_note_id)
        if st.session_state.current_note_id
        else "新規ノート"
    )
    st.session_state.unsaved_changes[key] = {"title": title, "content": content}


async def delete_note(client: httpx.AsyncClient, note_id: int) -> None:
    """
    ノートを削除する。

    :param client: 非同期HTTPクライアント
    :type client: httpx.AsyncClient
    :param note_id: 削除するノートのID
    :type note_id: int
    """
    try:
        url = f"{BACKEND_API_URL}{note_id}"
        response = await client.delete(url)
        response.raise_for_status()

        st.success("ノートを削除しました。")
        await get_notes()

        st.session_state.current_note_id = None
        st.session_state.note_title = ""
        st.session_state.markdown_text = ""
        st.session_state.selected_note = None
        st.session_state.show_new_note = False

    except httpx.HTTPStatusError as e:
        error_detail = e.response.text
        st.error(f"ノートの削除に失敗しました: {e}\n詳細: {error_detail}")
    except Exception as e:
        st.error(f"予期せぬエラーが発生しました: {e}")


async def display_note_content() -> None:
    """
    ノートの内容を表示する。

    非同期関数。現在のノートのタイトルと本文を表示し、編集や保存を行うことができる。
    """
    if st.session_state.notes_df is None:
        await get_notes()

    async with httpx.AsyncClient() as client:
        note_title: str = st.text_input(
            "ノートのタイトル",
            value=st.session_state.note_title,
            key="note_title_input",
        )

        if note_title != st.session_state.note_title:
            st.session_state.note_title = note_title
            update_unsaved_changes(note_title, st.session_state.markdown_text)

        is_valid, error_message = validate_title(note_title)
        if not is_valid:
            st.error(error_message)

        st.write(f"タイトル文字数: {len(note_title)}/200")

        st.subheader("ノート")

        st.markdown(
            """
            <style>
            .stButton button[data-testid="delete-button"] {
                color: red;
                border-color: red;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
        with col1:
            edit_button = st.button("テキスト編集", use_container_width=True)
        with col2:
            preview_button = st.button("プレビュー表示", use_container_width=True)
        with col4:
            save_button = st.button("保存", key="save_button", use_container_width=True)
        with col5:
            delete_button = st.button(
                "ノートを削除",
                key="delete_button",
                use_container_width=True,
            )

        if preview_button:
            st.session_state.show_preview = True
        if edit_button:
            st.session_state.show_preview = False

        if not st.session_state.show_preview:
            markdown_text: str = st.text_area(
                "テキストをここに入力してください",
                value=st.session_state.markdown_text,
                height=500,
                key="markdown_input",
                max_chars=15000,
            )
            if markdown_text != st.session_state.markdown_text:
                st.session_state.markdown_text = markdown_text
                update_unsaved_changes(note_title, markdown_text)

            st.write(f"本文文字数: {len(markdown_text)}/15000")
        else:
            processed_text: str = preprocess_markdown(st.session_state.markdown_text)
            st.markdown(processed_text)

        if save_button:
            if is_valid:
                await save_note(client, note_title, st.session_state.markdown_text)
            else:
                st.error("タイトルが無効です。保存できません。")

        if delete_button:
            if st.session_state.current_note_id:
                await delete_note(client, st.session_state.current_note_id)
                st.rerun()
            else:
                st.warning("削除するノートが選択されていません。")


async def main() -> None:
    """
    メイン関数。

    非同期関数。ノートの選択、表示、編集、保存を行うインターフェースを提供する。
    """
    try:
        st.title("AIサポート学習帳")

        if "notes_df" not in st.session_state or st.session_state.notes_df is None:
            await get_notes()

        with st.sidebar:
            if "note_titles" in st.session_state and st.session_state.note_titles:
                options = st.session_state.note_titles.copy()
                if st.session_state.get("show_new_note", False):
                    options = ["新規ノート"] + options

                selected_note: Any = st.selectbox(
                    "ノートを選択",
                    options,
                    key="note_selector",
                    index=(
                        0
                        if st.session_state.get("show_new_note", False)
                        else options.index(st.session_state.selected_note)
                        if st.session_state.selected_note in options
                        else 0
                    ),
                )

                if selected_note != st.session_state.selected_note:
                    st.session_state.selected_note = selected_note
                    if selected_note != "新規ノート":
                        selected_note_data = st.session_state.notes_df[
                            st.session_state.notes_df["title"] == selected_note
                        ].iloc[0]
                        st.session_state.current_note_id = selected_note_data["id"]

                        current_id = str(st.session_state.current_note_id)
                        unsaved_changes = st.session_state.unsaved_changes
                        if current_id in unsaved_changes:
                            unsaved = unsaved_changes[current_id]
                            st.session_state.note_title = unsaved["title"]
                            st.session_state.markdown_text = unsaved["content"]
                        else:
                            st.session_state.note_title = selected_note_data["title"]
                            st.session_state.markdown_text = selected_note_data[
                                "content"
                            ]
                    else:
                        create_new_note()
                    st.rerun()

            if st.button("新規ノート作成", key="create_new_note_button"):
                st.session_state.show_new_note = True
                st.session_state.selected_note = "新規ノート"
                create_new_note()
                st.rerun()

        # 必ずdisplay_note_contentを呼び出す
        await display_note_content()

        if st.session_state.last_saved_note:
            st.session_state.selected_note = st.session_state.last_saved_note["title"]
            st.session_state.last_saved_note = None
            st.session_state.show_new_note = False
            st.rerun()

    except Exception as e:
        st.error(f"アプリケーションエラー: {e}")
        logger.error(f"Unhandled error in main: {e}", exc_info=True)


def run() -> None:
    """
    非同期メイン関数を実行する。
    """
    asyncio.run(main())


if __name__ == "__main__":
    from utils.sidebar import show_sidebar

    show_sidebar()
    run()
