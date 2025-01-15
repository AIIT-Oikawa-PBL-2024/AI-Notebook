import pytest
from unittest import mock
from app.utils.convert_mp4_to_mp3 import convert_mp4_to_mp3
from typing import Generator


@pytest.fixture
def mock_storage_client() -> Generator[mock.MagicMock, None, None]:
    with mock.patch("app.utils.convert_mp4_to_mp3.storage.Client") as mock_client:
        yield mock_client


@pytest.fixture
def mock_ffmpeg() -> Generator[mock.MagicMock, None, None]:
    with mock.patch("app.utils.convert_mp4_to_mp3.ffmpeg") as mock_ffmpeg:
        yield mock_ffmpeg


@pytest.fixture
def mock_os() -> Generator[mock.MagicMock, None, None]:
    with mock.patch("app.utils.convert_mp4_to_mp3.os") as mock_os:
        yield mock_os


@pytest.mark.asyncio
async def test_convert_mp4_to_mp3_success(
    mock_storage_client: mock.MagicMock, mock_ffmpeg: mock.MagicMock, mock_os: mock.MagicMock
) -> None:
    bucket_name = "test-bucket"
    file_name = "test_video.mp4"

    # モックのセットアップ
    mock_client = mock_storage_client.return_value
    mock_bucket = mock_client.bucket.return_value
    # blob は複数回呼ばれるため、それぞれの場合に対応するように side_effect を使用
    mock_blob = mock_bucket.blob.return_value
    mock_blob.exists.return_value = True

    # OSのパス関連モック
    mock_os.path.basename.return_value = "test_video.mp4"
    mock_os.path.normpath.side_effect = lambda x: x
    mock_os.path.startswith.return_value = True

    # FFmpegのモック設定
    mock_input = mock.MagicMock()
    mock_output = mock.MagicMock()
    mock_ffmpeg.input.return_value = mock_input
    mock_input.output.return_value = mock_output
    mock_output.run.return_value = None

    # テスト対象の関数を呼び出し
    result = await convert_mp4_to_mp3(bucket_name, file_name)

    # 呼び出しの検証
    mock_storage_client.assert_called_once()
    mock_client.bucket.assert_called_once_with(bucket_name)
    mock_bucket.blob.assert_any_call(file_name)
    mock_blob.download_to_filename.assert_called_once()

    mock_ffmpeg.input.assert_called_once_with("/tmp/test_video.mp4")
    mock_input.output.assert_called_once_with(
        "/tmp/test_video.mp3", format="mp3", acodec="libmp3lame"
    )
    mock_output.run.assert_called_once()

    mock_bucket.blob.assert_any_call("mp3/test_video.mp3")
    mock_blob.upload_from_filename.assert_called_once()

    mock_os.remove.assert_any_call("/tmp/test_video.mp4")
    mock_os.remove.assert_any_call("/tmp/test_video.mp3")

    assert result is True


@pytest.mark.asyncio
async def test_convert_mp4_to_mp3_upload_failure(
    mock_storage_client: mock.MagicMock, mock_ffmpeg: mock.MagicMock, mock_os: mock.MagicMock
) -> None:
    bucket_name = "test-bucket"
    file_name = "test_video.mp4"

    # モックのセットアップ
    mock_client = mock_storage_client.return_value
    mock_bucket = mock_client.bucket.return_value
    # blob は複数回呼ばれるため、それぞれの場合に対応するように side_effect を使用
    mock_blob = mock_bucket.blob.return_value
    mock_blob.exists.return_value = False

    # OSのパス関連モック
    mock_os.path.basename.return_value = "test_video.mp4"
    mock_os.path.normpath.side_effect = lambda x: x
    mock_os.path.startswith.return_value = True

    # FFmpegのモック設定
    mock_input = mock.MagicMock()
    mock_output = mock.MagicMock()
    mock_ffmpeg.input.return_value = mock_input
    mock_input.output.return_value = mock_output
    mock_output.run.return_value = None

    result = await convert_mp4_to_mp3(bucket_name, file_name)

    assert result is False
