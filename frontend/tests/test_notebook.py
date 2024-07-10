import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
from streamlit.testing.v1 import AppTest
import httpx
import pandas as pd
import os
import sys

# テスト対象のモジュールをインポート
# from app.pages import notebook as app

# プロジェクトルートのパスを取得
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# プロジェクトルートをPythonパスに追加
if project_root not in sys.path:
    sys.path.insert(0, project_root)

class TestStreamlitApp(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.at = AppTest.from_file("app/pages/notebook.py")
        self.at.run()

    async def test_all_buttons_functionality(self) -> None:
        # テキスト編集ボタンのテスト
        edit_button = self.at.button("テキスト編集")
        self.assertTrue(edit_button.exists())
        edit_button.click()
        self.assertFalse(self.at.session_state["show_preview"])

        # プレビュー表示ボタンのテスト
        preview_button = self.at.button("プレビュー表示")
        self.assertTrue(preview_button.exists())
        preview_button.click()
        self.assertTrue(self.at.session_state["show_preview"])

        # 保存ボタンのテスト
        save_button = self.at.button("保存")
        self.assertTrue(save_button.exists())
        with patch('app.pages.notebook.save_note', new_callable=AsyncMock) as mock_save:
            save_button.click()
            await asyncio.sleep(0)  # 非同期処理を待つ
            mock_save.assert_called_once()

        # 新規ノート作成ボタンのテスト
        new_note_button = self.at.button("新規ノート作成")
        self.assertTrue(new_note_button.exists())
        with patch('app.pages.notebook.create_new_note') as mock_create:
            new_note_button.click()
            mock_create.assert_called_once()
            self.assertTrue(self.at.session_state["show_new_note"])
            self.assertEqual(self.at.session_state["selected_note"], "新規ノート")

    async def test_sidebar_functionality(self) -> None:
        # サイドバーのノート選択機能のテスト
        self.at.session_state["note_titles"] = ["新規ノート", "テストノート1", "テストノート2"]
        selectbox = self.at.selectbox("ノートを選択")
        self.assertTrue(selectbox.exists())
        
        # 既存のノートを選択
        with patch('streamlit.experimental_rerun'):
            selectbox.set_value("テストノート1")
            await asyncio.sleep(0)  # 非同期処理を待つ
            self.assertEqual(self.at.session_state["selected_note"], "テストノート1")
        
        # 新規ノートを選択
        with patch('streamlit.experimental_rerun'):
            selectbox.set_value("新規ノート")
            await asyncio.sleep(0)  # 非同期処理を待つ
            self.assertEqual(self.at.session_state["selected_note"], "新規ノート")
            self.assertIsNone(self.at.session_state["current_note_id"])

    @patch('app.pages.notebook.process_summary', new_callable=AsyncMock)
    async def test_summary_processing(self, mock_process_summary: AsyncMock) -> None:
        # 関数のインポート
        from app.pages import notebook as app
        # サマリー処理のテスト
        self.at.session_state["processing_summary"] = True
        await app.display_note_content()
        mock_process_summary.assert_called_once()

    def test_title_and_content_input(self) -> None:
        # タイトル入力のテスト
        title_input = self.at.text_input("ノートのタイトル")
        self.assertTrue(title_input.exists())
        title_input.set_value("テストタイトル")
        self.assertEqual(self.at.session_state["note_title"], "テストタイトル")

        # 本文入力のテスト
        content_input = self.at.text_area("テキストをここに入力してください")
        self.assertTrue(content_input.exists())
        content_input.set_value("テスト本文")
        self.assertEqual(self.at.session_state["markdown_text"], "テスト本文")

    @patch('app.pages.notebook.update_unsaved_changes')
    def test_unsaved_changes(self, mock_update: MagicMock) -> None:
        # 未保存の変更の更新をテスト
        title_input = self.at.text_input("ノートのタイトル")
        title_input.set_value("新しいタイトル")
        mock_update.assert_called_with("新しいタイトル", self.at.session_state["markdown_text"])

        content_input = self.at.text_area("テキストをここに入力してください")
        content_input.set_value("新しい本文")
        mock_update.assert_called_with(self.at.session_state["note_title"], "新しい本文")

    def test_error_messages(self) -> None:
        # エラーメッセージの表示をテスト
        title_input = self.at.text_input("ノートのタイトル")
        
        # タイトルが空の場合
        title_input.set_value("")
        self.assertIn("タイトルは必須です。", self.at.error[0].value)

        # タイトルが長すぎる場合
        title_input.set_value("a" * 201)
        self.assertIn("タイトルは200文字以内で入力してください。", self.at.error[0].value)

    @patch('app.pages.notebook.preprocess_markdown')
    async def test_markdown_preview(self, mock_preprocess: MagicMock) -> None:
        # 関数のインポート
        from app.pages import notebook as app
        # マークダウンプレビュー機能のテスト
        mock_preprocess.return_value = "Processed Markdown"
        
        content_input = self.at.text_area("テキストをここに入力してください")
        content_input.set_value("# Test Markdown")
        
        preview_button = self.at.button("プレビュー表示")
        preview_button.click()
        
        self.assertTrue(self.at.session_state["show_preview"])
        mock_preprocess.assert_called_with("# Test Markdown")
        
        # display_note_contentを呼び出してマークダウンを更新
        await app.display_note_content()
        
        # マークダウンの表示をチェック
        markdown_elements = self.at.markdown
        self.assertTrue(any("Processed Markdown" in str(element.value) for element in markdown_elements))

    @patch('httpx.AsyncClient.get')
    async def test_get_notes_error_handling(self, mock_get: AsyncMock) -> None:
        # 関数のインポート
        from app.pages import notebook as app
        # get_notesのエラーハンドリングをテスト
        mock_get.side_effect = httpx.HTTPStatusError("Error", request=MagicMock(), response=MagicMock())
        
        with self.assertRaises(Exception):
            await app.get_notes()
        
        self.assertIn("ノート情報の取得に失敗しました", self.at.error[0].value)

    @patch('httpx.AsyncClient.put')
    @patch('httpx.AsyncClient.post')
    async def test_save_note_error_handling(self, mock_post: AsyncMock, mock_put: AsyncMock) -> None:
        # 関数のインポート
        from app.pages import notebook as app
        # save_noteのエラーハンドリングをテスト
        mock_post.side_effect = httpx.HTTPStatusError("Error", request=MagicMock(), response=MagicMock())
        mock_put.side_effect = httpx.HTTPStatusError("Error", request=MagicMock(), response=MagicMock())

        async with httpx.AsyncClient() as client:
            await app.save_note(client, "Test Title", "Test Content")

        self.assertIn("ノートの保存に失敗しました", self.at.error[0].value)

    async def test_create_and_post_new_note_error_handling(self) -> None:
        # 関数のインポート
        from app.pages import notebook as app
        # create_and_post_new_noteのエラーハンドリングをテスト
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.side_effect = Exception("Unexpected error")
            
            async with httpx.AsyncClient() as client:
                await app.create_and_post_new_note(client)

        self.assertIn("予期せぬエラーが発生しました", self.at.sidebar.error[0].value)

    def test_session_state_initialization(self) -> None:
        # 関数のインポート
        from app.pages import notebook as app
        # セッション状態の初期化をテスト
        app.init_session_state()
        expected_keys = [
            "note_title", "markdown_text", "show_preview", "current_note_id",
            "notes_df", "note_titles", "selected_files", "processing_summary",
            "summary_result", "user_id", "unsaved_changes", "last_saved_note",
            "selected_note", "show_new_note"
        ]
        for key in expected_keys:
            self.assertIn(key, self.at.session_state)

    @patch('app.pages.notebook.preprocess_markdown')
    async def test_markdown_preprocessing(self, mock_preprocess: MagicMock) -> None:
        # 関数のインポート
        from app.pages import notebook as app
        # マークダウンの前処理をテスト
        test_markdown = "# Header\n- List item"
        mock_preprocess.return_value = "Processed Markdown"
        
        self.at.session_state["markdown_text"] = test_markdown
        self.at.session_state["show_preview"] = True
        
        # display_note_content関数を呼び出す
        await app.display_note_content()
        
        mock_preprocess.assert_called_with(test_markdown)
        # マークダウンの表示をチェック
        markdown_elements = self.at.markdown
        self.assertTrue(any("Processed Markdown" in str(element.value) for element in markdown_elements))

    async def test_process_summary_error_handling(self) -> None:
        # 関数のインポート
        from app.pages import notebook as app
        # process_summaryのエラーハンドリングをテスト
        with patch('app.pages.notebook.create_pdf_to_markdown_summary', new_callable=AsyncMock) as mock_summary:
            mock_summary.side_effect = Exception("Summary processing error")
            
            self.at.session_state["processing_summary"] = True
            self.at.session_state["selected_files"] = ["test.pdf"]
            
            await app.process_summary()
            
            self.assertFalse(self.at.session_state["processing_summary"])
            self.assertIn("エラーが発生しました", self.at.session_state["summary_result"])

    def test_update_unsaved_changes(self) -> None:
        # 関数のインポート
        from app.pages import notebook as app
        # 未保存の変更の更新をテスト
        self.at.session_state["current_note_id"] = 1
        app.update_unsaved_changes("New Title", "New Content")
        
        self.assertIn("1", self.at.session_state["unsaved_changes"])
        self.assertEqual(self.at.session_state["unsaved_changes"]["1"]["title"], "New Title")
        self.assertEqual(self.at.session_state["unsaved_changes"]["1"]["content"], "New Content")

    @patch('streamlit.experimental_rerun')
    def test_note_selection_rerun(self, mock_rerun: MagicMock) -> None:
        # ノート選択時のrerunをテスト
        self.at.session_state["note_titles"] = ["Note 1", "Note 2"]
        self.at.session_state["notes_df"] = pd.DataFrame({
            "id": [1, 2],
            "title": ["Note 1", "Note 2"],
            "content": ["Content 1", "Content 2"]
        })
        
        selectbox = self.at.selectbox("ノートを選択")
        selectbox.set_value("Note 2")
        
        self.assertEqual(self.at.session_state["selected_note"], "Note 2")
        self.assertEqual(self.at.session_state["current_note_id"], 2)
        mock_rerun.assert_called_once()

    async def test_character_count_display(self) -> None:
        # 関数のインポート
        from app.pages import notebook as app
        # 文字数表示のテスト
        title_input = self.at.text_input("ノートのタイトル")
        title_input.set_value("Test Title")
        
        content_input = self.at.text_area("テキストをここに入力してください")
        content_input.set_value("Test Content")
        
        # display_note_content関数を呼び出して更新を反映
        await app.display_note_content()
        
        # 文字数表示をチェック
        all_elements = (
            list(self.at.text) + 
            list(self.at.markdown) + 
            list(self.at.caption) +
            list(self.at.subheader)
            )

        all_text = " ".join(str(element.value) for element in all_elements)
    
        title_count_displayed = "タイトル文字数: 10/200" in all_text
        content_count_displayed = "本文文字数: 12/15000" in all_text
    
        self.assertTrue(title_count_displayed, "タイトルの文字数が正しく表示されていません")
        self.assertTrue(content_count_displayed, "本文の文字数が正しく表示されていません")

if __name__ == '__main__':
    unittest.main()