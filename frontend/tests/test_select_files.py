import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.pages.select_files import (
    get_files_list,
    show_files_list_df,
    utc_to_jst,
    update,
    get_selected_files,
    update_note_name,
)
import streamlit as st
import pandas as pd


# get_files_list 関数のテスト
@pytest.mark.asyncio
async def test_get_files_list(mocker: MagicMock) -> None:
    # モックされたレスポンスを設定
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"file_name": "file1.txt", "created_at": "2023-06-21T00:00:00Z"},
        {"file_name": "file2.txt", "created_at": "2023-06-21T01:00:00Z"},
    ]

    # httpx.AsyncClient の get メソッドをモック
    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    # 関数を呼び出して結果を検証
    files = await get_files_list()
    assert len(files) == 2
    assert files[0] == {"file_name": "file1.txt", "created_at": "2023-06-21T00:00:00Z"}


# show_files_list_df 関数のテスト
@pytest.mark.asyncio
async def test_show_files_list_df(mocker: MagicMock) -> None:
    # streamlit のセッション状態をモック
    mock_session_state = MagicMock()
    mock_session_state.df = None
    mock_session_state.df_updated = False

    mocker.patch("streamlit.session_state", mock_session_state)

    # get_files_list 関数をモック
    mocker.patch(
        "app.pages.select_files.get_files_list",
        new_callable=AsyncMock,
        return_value=[
            {"file_name": "file1.txt", "created_at": "2023-06-21T00:00:00Z"},
            {"file_name": "file2.txt", "created_at": "2023-06-21T01:00:00Z"},
        ],
    )

    # 関数を呼び出して結果を検証
    await show_files_list_df()
    assert mock_session_state.df is not None
    assert len(mock_session_state.df) == 2


# 日本時間に変換する関数のテスト
def test_utc_to_jst() -> None:
    utc_time = "2023-06-21T00:00:00Z"
    jst_time = utc_to_jst(utc_time)
    assert jst_time == "2023-06-21 09:00:00"


# update 関数のテスト
def test_update(mocker: MagicMock) -> None:
    # 実際のデータフレームを使用
    df = pd.DataFrame(
        {
            "file_name": ["file1.txt", "file2.txt"],
            "created_at": ["2023-06-21 00:00:00", "2023-06-21 01:00:00"],
        }
    )

    # モックされたセッション状態を辞書として設定
    mock_session_state = {
        "changes": {
            "edited_rows": {
                0: {"file_name": "updated_file1.txt"},
                1: {"created_at": "2023-06-21 10:00:00"},
            }
        },
        "df": df,
        "df_updated": False,
    }

    # session_state を辞書としてモック
    with patch.dict("streamlit.session_state", mock_session_state):
        # 関数を呼び出して結果を検証
        update()

        # データフレームの更新を検証
        assert st.session_state["df"].at[0, "file_name"] == "updated_file1.txt"
        assert st.session_state["df"].at[1, "created_at"] == "2023-06-21 10:00:00"

        # df_updated が True に設定されているかを検証
        assert st.session_state["df_updated"] == True


# get_selected_files 関数のテスト
def test_get_selected_files(mocker: MagicMock) -> None:
    # 実際のデータフレームを使用
    df = pd.DataFrame(
        {
            "file_name": ["file1.txt", "file2.txt", "file3.txt"],
            "select": [True, False, True],
        }
    )

    # モックされたセッション状態を辞書として設定
    mock_session_state = {"df": df}

    # session_state を辞書としてモック
    with patch.dict("streamlit.session_state", mock_session_state):
        # 関数を呼び出して結果を検証
        selected_files = get_selected_files()

        # 選択されたファイルが正しく取得されているかを検証
        assert selected_files == ["file1.txt", "file3.txt"]


# get_selected_files 関数のテスト（データフレームが空の場合）
def test_get_selected_files_empty_df(mocker: MagicMock) -> None:
    # モックされたセッション状態を辞書として設定
    mock_session_state = {"df": None}

    # session_state を辞書としてモック
    with patch.dict("streamlit.session_state", mock_session_state):
        # 関数を呼び出して結果を検証
        selected_files = get_selected_files()

        # 空のリストが返されることを検証
        assert selected_files == []


# update_note_name 関数のテスト
def test_update_note_name(mocker: MagicMock) -> None:
    # モックされたセッション状態を設定
    mock_session_state = {"note_input": "New Note Title"}

    # session_state を辞書としてモック
    with patch.dict("streamlit.session_state", mock_session_state):
        # 関数を呼び出して結果を検証
        update_note_name()

        # note_nameが正しく更新されているかを検証
        assert st.session_state.note_name == "New Note Title"
