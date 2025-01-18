import pytest
from unittest.mock import patch, MagicMock
from google.api_core.exceptions import InternalServerError

# モジュールの再読み込みのためにimportlibをインポート
import importlib

# vertexai.initをモックする
with patch("app.utils.gemini_extract_text_from_audio.vertexai.init") as mock_vertexai_init:
    # モジュールを再読み込みして、モックと環境変数が適用されるようにする
    import app.utils.gemini_extract_text_from_audio

    importlib.reload(app.utils.gemini_extract_text_from_audio)
    from app.utils.gemini_extract_text_from_audio import extract_text_from_audio

    @pytest.mark.asyncio
    @patch("app.utils.gemini_extract_text_from_audio.GenerativeModel")
    async def test_extract_text_from_audio_success(mock_model_class: MagicMock) -> None:
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "test_text"
        # 非同期呼び出しに対応するため、generate_content を同期的に返すように設定
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model_instance

        result = await extract_text_from_audio("test_bucket", "test_audio.mp3")
        assert result == "test_text"

    @pytest.mark.asyncio
    @patch("app.utils.gemini_extract_text_from_audio.GenerativeModel")
    async def test_extract_text_from_audio_unsupported_format(mock_model_class: MagicMock) -> None:
        with pytest.raises(
            InternalServerError, match="音声の文字起こしエラー: Unsupported audio file format."
        ):
            await extract_text_from_audio("test_bucket", "test_audio.txt")

    @pytest.mark.asyncio
    @patch("app.utils.gemini_extract_text_from_audio.GenerativeModel")
    async def test_extract_text_from_audio_internal_server_error(
        mock_model_class: MagicMock,
    ) -> None:
        mock_model_instance = MagicMock()
        mock_model_class.return_value = mock_model_instance
        mock_model_instance.generate_content.side_effect = Exception("Test error")

        with pytest.raises(InternalServerError, match="音声の文字起こしエラー: Test error"):
            await extract_text_from_audio("test_bucket", "test_audio.mp3")
