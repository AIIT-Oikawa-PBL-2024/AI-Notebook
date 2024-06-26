import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.pages.select_files import (
    get_files_list,
    show_files_list_df,
    time_format,
    update,
    get_selected_files,
    update_note_name,
    show_select_files_page,
)
import streamlit as st
import pandas as pd
import logging
import httpx
from streamlit.testing.v1 import AppTest

# ストリームリットのエラーメッセージをモック
st.error = MagicMock()

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# バックエンドAPIのURL
BACKEND_DEV_API_URL = "http://localhost:8000/files/"


# get_files_list 関数のテスト
@pytest.mark.asyncio
async def test_get_files_list_success(mocker: MagicMock) -> None:
    # モックされたレスポンスを設定
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "id": 1,
            "user_id": 1,
            "file_name": "file1.txt",
            "created_at": "2023-06-21T00:00:00Z",
            "file_size": 1234,
        },
        {
            "id": 2,
            "user_id": 2,
            "file_name": "file2.txt",
            "created_at": "2023-06-21T01:00:00Z",
            "file_size": 5678,
        },
    ]
    mock_response.raise_for_status.return_value = None

    # httpx.AsyncClient の get メソッドをモック
    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    # 関数を呼び出して結果を検証
    files = await get_files_list()
    assert len(files) == 2
    assert files[0] == {
        "id": 1,
        "user_id": 1,
        "file_name": "file1.txt",
        "created_at": "2023-06-21T00:00:00Z",
        "file_size": 1234,
    }
    assert files[1] == {
        "id": 2,
        "user_id": 2,
        "file_name": "file2.txt",
        "created_at": "2023-06-21T01:00:00Z",
        "file_size": 5678,
    }


# get_files_list 関数のテスト（HTTP Status Error）
@pytest.mark.asyncio
async def test_get_files_list_http_status_error(mocker: MagicMock) -> None:
    # httpx.HTTPStatusError を発生させるモック
    request = httpx.Request("GET", BACKEND_DEV_API_URL)
    response = httpx.Response(status_code=500, request=request)
    http_status_error = httpx.HTTPStatusError(
        "HTTP error", request=request, response=response
    )

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = http_status_error

    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    # Streamlitのエラーメッセージ関数をモック
    mock_st_error = mocker.patch("streamlit.error")

    # 関数を呼び出してエラーメッセージが表示されることを検証
    files = await get_files_list()
    assert files == []
    mock_st_error.assert_called_with(
        "ファイル一覧の取得に失敗しました(HTTP Status Error)"
    )


# get_files_list 関数のテスト（Request Error）
@pytest.mark.asyncio
async def test_get_files_list_request_error(mocker: MagicMock) -> None:
    # httpx.RequestError を発生させるモック
    mocker.patch(
        "httpx.AsyncClient.get",
        side_effect=httpx.RequestError("Request error", request=None),
    )

    # Streamlitのエラーメッセージ関数をモック
    mock_st_error = mocker.patch("streamlit.error")

    # 関数を呼び出してエラーメッセージが表示されることを検証
    files = await get_files_list()
    assert files == []
    mock_st_error.assert_called_with("ファイル一覧の取得に失敗しました(Request Error)")


# get_files_list 関数のテスト（その他の例外）
@pytest.mark.asyncio
async def test_get_files_list_general_exception(mocker: MagicMock) -> None:
    # その他の例外を発生させるモック
    mocker.patch("httpx.AsyncClient.get", side_effect=Exception("General error"))

    # Streamlitのエラーメッセージ関数をモック
    mock_st_error = mocker.patch("streamlit.error")

    # 関数を呼び出してエラーメッセージが表示されることを検証
    files = await get_files_list()
    assert files == []
    mock_st_error.assert_called_with("ファイル一覧の取得に失敗しました(Error)")


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
            {
                "id": 1,
                "user_id": 1,
                "file_name": "file1.txt",
                "created_at": "2023-06-21T00:00:00Z",
                "file_size": 1234,
            },
            {
                "id": 2,
                "user_id": 2,
                "file_name": "file2.txt",
                "created_at": "2023-06-21T01:00:00Z",
                "file_size": 5678,
            },
        ],
    )

    # 関数を呼び出して結果を検証
    await show_files_list_df()
    assert mock_session_state.df is not None
    assert len(mock_session_state.df) == 2


# 時刻フォーマットを変換する関数のテスト
def test_time_format() -> None:
    jst_str = "2023-06-21T00:00:00Z"
    jst_time = time_format(jst_str)
    assert jst_time == "2023-06-21 00:00:00"


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


# show_select_files_page 関数のテスト
@pytest.mark.asyncio
async def test_show_select_files_page() -> None:
    # テスト用のAppTestインスタンスを作成
    at = AppTest.from_file("app/pages/select_files.py")

    # アプリを実行
    at.run()

    # 初期状態の確認
    print("Initial state:")
    print(f"Headers: {[header.value for header in at.header]}")
    print(f"Buttons: {[button.label for button in at.button]}")
    print(f"Text inputs: {len(at.text_input)}")
    print(f"Session state: {at.session_state}")

    assert at.header[0].value == "AIノートを作成"
    assert "ファイル一覧を取得" in [button.label for button in at.button]
    assert "リセット" in [button.label for button in at.button]

    # "ファイル一覧を取得"ボタンをクリック
    file_list_button = next(
        button for button in at.button if button.label == "ファイル一覧を取得"
    )
    file_list_button.click()
    at.run()

    # セッション状態を更新（ファイルが選択された状態をシミュレート）
    at.session_state["df"] = pd.DataFrame(
        {"file_name": ["file1.txt", "file2.txt"], "select": [True, True]}
    )
    at.session_state["df_updated"] = True

    # アプリを再実行
    at.run()

    # 更新後の状態確認
    print("\nUpdated state:")
    print(f"Headers: {[header.value for header in at.header]}")
    print(f"Buttons: {[button.label for button in at.button]}")
    print(f"Text inputs: {len(at.text_input)}")
    print(f"Session state: {at.session_state}")

    # テキスト入力フィールドの存在を確認
    assert len(at.text_input) > 0, "テキスト入力フィールドが見つかりません"

    if len(at.text_input) > 0:
        print(f"Text input label: {at.text_input[0].label}")
        assert (
            "AIで作成するノートのタイトルを100文字以内で入力してEnterキーを押して下さい"
            in at.text_input[0].label
        )

    # "AIノートを作成"ボタンが表示されないことを確認（テキストが入力されていない場合）
    button_labels = [button.label for button in at.button]
    print(f"Button labels: {button_labels}")
    assert (
        "AIノートを作成" not in button_labels
    ), "AIノートを作成'ボタンが表示されていますが、テキストが入力されていません"

    # テキスト入力フィールドに値を入力
    at.session_state["note_input"] = "ノートのタイトル"
    at.session_state["note_name"] = "ノートのタイトル"
    at.run()

    # 再度状態を確認
    print("\nState after text input:")
    print(f"Headers: {[header.value for header in at.header]}")
    print(f"Buttons: {[button.label for button in at.button]}")
    print(f"Text inputs: {len(at.text_input)}")
    print(f"Session state: {at.session_state}")

    # テキスト入力フィールドの値を確認
    assert (
        at.session_state["note_input"] == "ノートのタイトル"
    ), f"Expected 'ノートのタイトル', but got {at.session_state['note_input']}"

    # "AIノートを作成"ボタンが表示されることを確認（テキストが入力された場合）
    button_labels = [button.label for button in at.button]
    print(f"Button labels: {button_labels}")
    assert (
        "AIノートを作成" in button_labels
    ), "'AIノートを作成'ボタンが表示されていません"

    # "AIノートを作成"ボタンをクリック
    create_note_button = next(
        button for button in at.button if button.label == "AIノートを作成"
    )
    create_note_button.click()
    at.run()

    # ページが遷移したことを確認
    assert at.session_state["page"] == "pages/study_ai_note.py"


# リセットボタンのテスト
@pytest.mark.asyncio
async def test_reset_button() -> None:
    # テスト用のAppTestインスタンスを作成
    at = AppTest.from_file("app/pages/select_files.py")

    # アプリを実行
    at.run()

    # "ファイル一覧を取得"ボタンをクリック
    file_list_button = next(
        button for button in at.button if button.label == "ファイル一覧を取得"
    )
    file_list_button.click()
    at.run()

    # セッション状態を更新（ファイルが選択された状態をシミュレート）
    at.session_state["df"] = pd.DataFrame(
        {"file_name": ["file1.txt", "file2.txt"], "select": [True, True]}
    )
    at.session_state["df_updated"] = True

    # アプリを再実行
    at.run()

    # リセットボタンをクリック
    reset_button = next(button for button in at.button if button.label == "リセット")
    reset_button.click()
    at.run()

    # 入力がリセットされたことを確認
    assert at.session_state["note_name"] == ""
    assert at.session_state["selected_files"] == []
