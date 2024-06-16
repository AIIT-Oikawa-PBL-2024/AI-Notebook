import pytest
from streamlit.testing.v1 import AppTest
from PIL import Image
import os

@pytest.fixture
def mock_image(monkeypatch):
    """画像をモックし、テスト用の画像を作成する"""
    img = Image.new('RGB', (100, 100), color = 'red')
    img.save('mock_image.jpg')

    def mock_image_show(*args, **kwargs):
        return Image.open('mock_image.jpg')

    monkeypatch.setattr(Image, 'open', mock_image_show)
    
    yield
    
    # テスト後にモック画像を削除
    os.remove('mock_image.jpg')

@pytest.fixture
def at(mock_image):
    return AppTest.from_file("main.py").run()

def test_image_displayed(at):
    """画像が表示されているかテスト"""
    assert len(at.image) == 1
    assert at.image[0].width == 100  # モック画像のサイズ

def test_sidebar_content(at):
    """サイドバーの内容をテスト"""
    sidebar = at.sidebar.markdown[0].value
    assert "Home" in sidebar
    assert "Upload Files" in sidebar
    assert "🏠" in sidebar  # ホームアイコン
    assert "1️⃣" in sidebar  # アップロードファイルアイコン

def test_page_links(at):
    """ページリンクが正しいかテスト"""
    sidebar = at.sidebar.markdown[0].value
    assert 'href="main.py"' in sidebar
    assert 'href="pages/upload_files.py"' in sidebar

def test_no_main_area_text(at):
    """メインエリアにテキストが表示されていないことをテスト"""
    assert len(at.markdown) == 0