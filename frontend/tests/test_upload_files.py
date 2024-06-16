import io
import pytest
from unittest.mock import patch, MagicMock
import responses
from streamlit.testing.v1 import AppTest

# テスト対象のアプリをインポート
import app

@pytest.fixture
def at():
    return AppTest.from_file("app.py").run()

def test_sidebar_links(at):
    """サイドバーのリンクをテスト"""
    sidebar = at.sidebar.markdown[0].value
    assert "Home" in sidebar
    assert "Upload Files" in sidebar
    assert 'href="main.py"' in sidebar
    assert 'href="pages/upload_files.py"' in sidebar

def test_is_valid_file():
    """is_valid_file関数のテスト"""
    valid_file = MagicMock(name="test.pdf", size=1024*1024)
    assert app.is_valid_file(valid_file) == True

    invalid_ext_file = MagicMock(name="test.txt", size=1024*1024)
    assert app.is_valid_file(invalid_ext_file) == False

    oversized_file = MagicMock(name="large.pdf", size=300*1024*1024)
    assert app.is_valid_file(oversized_file) == False

@pytest.mark.parametrize("files,expected_valid", [
    ([("valid.pdf", 1024*1024)], 1),
    ([("invalid.txt", 1024*1024)], 0),
    ([("valid1.pdf", 1024*1024), ("valid2.jpg", 2*1024*1024)], 2),
    ([("valid1.pdf", 1024*1024), ("valid1.pdf", 1024*1024)], 1),  # Duplicate file
    ([("large.pdf", 300*1024*1024)], 0),
])
def test_file_upload(at, files, expected_valid):
    """ファイルアップロードのテスト"""
    with patch('streamlit.file_uploader') as mock_uploader:
        mock_files = []
        for name, size in files:
            mock_file = MagicMock(name=name, size=size)
            mock_file.getvalue.return_value = b"test content"
            mock_files.append(mock_file)
        
        mock_uploader.return_value = mock_files
        at.rerun()
        
        success_messages = [msg for msg in at.message if "Valid file:" in str(msg.value)]
        assert len(success_messages) == expected_valid

@responses.activate
def test_submit_button(at):
    """Submitボタンのテスト"""
    responses.add(responses.POST, 'http://www.test.com', status=200)

    with patch('streamlit.file_uploader') as mock_uploader:
        mock_file = MagicMock(name="test.pdf", size=1024*1024)
        mock_file.getvalue.return_value = b"test content"
        mock_uploader.return_value = [mock_file]

        at.rerun()
        submit_button = at.button[0]
        submit_button.click().run()

        assert "Files successfully uploaded!" in str(at.message[-1])

@responses.activate
def test_submit_button_error(at):
    """Submitボタンのエラーハンドリングテスト"""
    responses.add(responses.POST, 'http://www.test.com', status=500)

    with patch('streamlit.file_uploader') as mock_uploader:
        mock_file = MagicMock(name="test.pdf", size=1024*1024)
        mock_file.getvalue.return_value = b"test content"
        mock_uploader.return_value = [mock_file]

        at.rerun()
        submit_button = at.button[0]
        submit_button.click().run()

        assert "Error occurred. Status code: 500" in str(at.message[-1])

def test_no_files_warning(at):
    """ファイルがない場合の警告メッセージテスト"""
    with patch('streamlit.file_uploader', return_value=[]):
        at.rerun()
        assert "No valid files to submit." in str(at.message[-1])