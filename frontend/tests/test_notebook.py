import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import pandas as pd
import streamlit as st
from typing import Dict, Any, List, Tuple, cast, Generator
from streamlit.runtime.state.session_state_proxy import SessionStateProxy
import httpx

from app.pages.notebook import (
    init_session_state,
    preprocess_markdown,
    validate_title,
    get_notes,
    create_new_note,
    save_note,
    create_and_post_new_note,
    update_unsaved_changes,
    display_note_content,
    main,
)

class MockSessionState(dict):
    def __getattr__(self, key: str) -> Any:
        return self[key]
    
    def __setattr__(self, key: str, value: Any) -> None:
        self[key] = value

@pytest.fixture
def mock_session_state() -> Generator[MockSessionState, None, None]:
    session_state = MockSessionState({
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
    })
    with patch("streamlit.session_state", session_state):
        yield session_state

def test_init_session_state(mock_session_state: MockSessionState) -> None:
    # 目的：init_session_state 関数が正しくセッション状態を初期化することを確認する
    # 1. init_session_state 関数を呼び出す
    # 2. 期待されるすべてのキーがセッション状態に存在することを確認する
    init_session_state()
    expected_keys: List[str] = [
        "note_title", "markdown_text", "show_preview", "current_note_id",
        "notes_df", "note_titles", "user_id", "unsaved_changes",
        "last_saved_note", "selected_note", "show_new_note",
    ]
    for key in expected_keys:
        assert key in mock_session_state

def test_preprocess_markdown() -> None:
    # 目的: preprocess_markdown 関数が正しくマークダウンテキストを処理することを確認する
    # 1. サンプルの入力テキストを用意する
    # 2. preprocess_markdown 関数を呼び出す
    # 3. 関数の出力が期待される結果と一致することを確認する
    input_text: str = "##Header\n-List item\n1.Numbered item\n>Quote"
    expected_output: str = "## Header  \n- List item  \n1. Numbered item  \n> Quote  "
    assert preprocess_markdown(input_text) == expected_output

def test_validate_title() -> None:
    # 目的: validate_title 関数が様々な入力に対して正しく動作することを確認する
    # 1. 空文字列、スペースのみ、長すぎるタイトル、有効なタイトルをテストする
    # 2. 各ケースで validate_title 関数を呼び出し、期待される結果を確認する
    assert validate_title("") == (False, "タイトルは必須です。")
    assert validate_title("   ") == (False, "タイトルは必須です。")
    assert validate_title("a" * 201) == (False, "タイトルは200文字以内で入力してください。")
    assert validate_title("Valid Title") == (True, "")

@pytest.mark.asyncio
async def test_get_notes(mock_session_state: MockSessionState) -> None:
    # 目的: get_notes 関数が正しくノート情報を取得し、セッション状態を更新することを確認する
    # 1. APIレスポンスをモックする
    # 2. get_notes 関数を呼び出す
    # 3. セッション状態の notes_df が正しく更新されていることを確認する
    # 4. note_titles が正しく設定されていることを確認する
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "id": 1,
            "title": "Test Note",
            "content": "Test Content",
            "user_id": 1,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        }
    ]
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        await get_notes()

    assert isinstance(mock_session_state.notes_df, pd.DataFrame)
    assert len(mock_session_state.notes_df) == 1
    assert mock_session_state.note_titles == ["Test Note"]

def test_create_new_note(mock_session_state: MockSessionState) -> None:
    # 目的: create_new_note 関数が新しいノートを正しく作成することを確認する
    # 1. モックセッション状態に unsaved_changes を設定する
    # 2. create_new_note 関数を呼び出す
    # 3. セッション状態が正しく更新されていることを確認する
    mock_session_state.unsaved_changes = {"新規ノート": {"title": "New Title", "content": "New Content"}}
    create_new_note()
    assert mock_session_state.current_note_id is None
    assert mock_session_state.note_title == "New Title"
    assert mock_session_state.markdown_text == "New Content"
    assert not mock_session_state.show_preview

@pytest.mark.asyncio
async def test_save_note(mock_session_state: MockSessionState) -> None:
    # 目的: save_note 関数が正しく動作することを確認する
    # 1. APIクライアントとレスポンスをモックする
    # 2. セッション状態を設定する
    # 3. save_note 関数を呼び出す
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": 1, "title": "Test Note"}
    mock_response.raise_for_status.return_value = None
    mock_client.post.return_value = mock_response
    mock_client.put.return_value = mock_response

    mock_session_state.user_id = 1
    mock_session_state.notes_df = pd.DataFrame()
    mock_session_state.current_note_id = None

    with patch("streamlit.success"):
        with patch("app.pages.notebook.get_notes"):
            await save_note(mock_client, "Test Note", "Test Content")

@pytest.mark.asyncio
async def test_create_and_post_new_note(mock_session_state: MockSessionState) -> None:
    # 目的: create_and_post_new_note 関数が新しいノートを作成し、正しくポストすることを確認する
    # 1. APIクライアントとレスポンスをモックする
    # 2. セッション状態を設定する
    # 3. create_and_post_new_note 関数を呼び出す
    # 注意: このテストでは関数の実行のみを確認し、結果の検証は行っていない
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": 1, "title": "新規ノート", "content": ""}
    mock_response.raise_for_status.return_value = None
    mock_client.post.return_value = mock_response

    mock_session_state.user_id = 1

    with patch("streamlit.sidebar.success"):
        with patch("app.pages.notebook.get_notes"):
            await create_and_post_new_note(mock_client)

def test_update_unsaved_changes(mock_session_state: MockSessionState) -> None:
    # 目的: update_unsaved_changes 関数が未保存の変更を正しく更新することを確認する
    # 1. セッション状態に current_note_id を設定する
    # 2. update_unsaved_changes 関数を呼び出す
    # 3. unsaved_changes が正しく更新されていることを確認する
    mock_session_state.current_note_id = 1
    update_unsaved_changes("Test Title", "Test Content")
    assert mock_session_state.unsaved_changes == {"1": {"title": "Test Title", "content": "Test Content"}}

@pytest.mark.asyncio
async def test_display_note_content(mock_session_state: MockSessionState) -> None:
    # 目的: display_note_content 関数が正しくノート内容を表示することを確認する
    # 1. セッション状態を設定する
    # 2. Streamlitの各コンポーネントをモックする
    # 3. display_note_content 関数を呼び出す
    # 4. セッション状態が正しく更新されていることを確認する
    mock_session_state.notes_df = pd.DataFrame({"title": ["Test Note"], "content": ["Test Content"]})
    mock_session_state.note_title = "Test Note"
    mock_session_state.markdown_text = "Test Content"
    mock_session_state.show_preview = False

    with patch("streamlit.text_input", return_value="Test Note") as mock_text_input:
        with patch("streamlit.text_area", return_value="Updated Content") as mock_text_area:
            with patch("streamlit.button", return_value=False) as mock_button:
                with patch("httpx.AsyncClient"):
                    with patch("app.pages.notebook.update_unsaved_changes"):
                        await display_note_content()

    assert mock_session_state.markdown_text == "Updated Content"
    mock_text_input.assert_called_once()
    mock_text_area.assert_called_once()
    mock_button.assert_called()

@pytest.mark.asyncio
async def test_main(mock_session_state: MockSessionState) -> None:
    # 目的: main 関数が正しく動作することを確認する
    # 1. セッション状態を設定する
    # 2. Streamlitの各コンポーネントと主要な関数をモックする
    # 3. main 関数を呼び出す
    # 4. display_note_content が呼び出されたことを確認する
    mock_session_state.notes_df = None
    mock_session_state.note_titles = ["Test Note"]
    mock_session_state.selected_note = "Test Note"
    
    with patch("streamlit.set_page_config"):
        with patch("streamlit.title"):
            with patch("streamlit.sidebar.selectbox", return_value="Test Note"):
                with patch("app.pages.notebook.display_note_content") as mock_display_note_content:
                    with patch("app.pages.notebook.get_notes"):
                        await main()

    mock_display_note_content.assert_called_once()

if __name__ == "__main__":
    pytest.main(["-v", "-p", "no:warnings"])