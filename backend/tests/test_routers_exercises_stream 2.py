import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app
from app.routers.exercises_stream import request_content
from google.api_core.exceptions import GoogleAPIError, InvalidArgument, NotFound

client = TestClient(app)


# 正常系のテスト
@pytest.mark.asyncio
@patch("app.routers.exercises_stream.generate_content_stream")
async def test_request_content_normal(mock_generate_content_stream: AsyncMock) -> None:
    # モックの設定
    mock_response = AsyncMock()
    mock_response.__aiter__.return_value = ["content part 1", "content part 2"]
    mock_generate_content_stream.return_value = mock_response

    # リクエストデータ
    files = ["file1.txt", "file2.txt"]

    # リクエストの送信
    response = client.post("/exercises/request_stream", json=files)

    # レスポンスの検証
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

    # StreamingResponseの内容を検証
    expected_content = "".join(part for part in ["content part 1", "content part 2"])
    assert response.text == expected_content

    # generate_content_streamが正しい引数で呼ばれたことを検証
    mock_generate_content_stream.assert_called_once_with(files)

    # 異常系のテスト - GoogleAPIError
    @pytest.mark.asyncio
    @patch("app.routers.exercises_stream.generate_content_stream")
    async def test_request_content_google_api_error(
        mock_generate_content_stream: AsyncMock,
    ) -> None:
        # モックの設定
        mock_generate_content_stream.side_effect = GoogleAPIError("Google API error")

        # リクエストデータ
        files = ["file1.txt", "file2.txt"]

        # リクエストの送信
        response = client.post("/exercises/request_stream", json=files)

        # レスポンスの検証
        assert response.status_code == 500
        assert response.json() == {"detail": "Google API error"}


# 異常系のテスト - InvalidArgument
@pytest.mark.asyncio
@patch("app.routers.exercises_stream.generate_content_stream")
async def test_request_content_invalid_argument(
    mock_generate_content_stream: AsyncMock,
) -> None:
    # モックの設定
    mock_generate_content_stream.side_effect = InvalidArgument("Invalid argument error")

    # リクエストデータ
    files = ["file1.txt", "file2.txt"]

    # リクエストの送信
    response = client.post("/exercises/request_stream", json=files)

    # レスポンスの検証
    assert response.status_code == 400
    assert response.json() == {
        "detail": "ファイル名の形式が無効です。有効なファイル名を指定してください。"
    }


# 異常系のテスト - NotFound
@pytest.mark.asyncio
@patch("app.routers.exercises_stream.generate_content_stream")
async def test_request_content_not_found(
    mock_generate_content_stream: AsyncMock,
) -> None:
    # モックの設定
    mock_generate_content_stream.side_effect = NotFound("File not found")

    # リクエストデータ
    files = ["file1.txt", "file2.txt"]

    # リクエストの送信
    response = client.post("/exercises/request_stream", json=files)

    # レスポンスの検証
    assert response.status_code == 404
    assert response.json() == {
        "detail": "指定されたファイルがGoogle Cloud Storageに見つかりません。"
        + "ファイル名を再確認してください。"
    }


# 異常系のテスト - GoogleAPIError
@pytest.mark.asyncio
@patch("app.routers.exercises_stream.generate_content_stream")
async def test_request_content_google_api_error(
    mock_generate_content_stream: AsyncMock,
) -> None:
    # モックの設定
    mock_generate_content_stream.side_effect = GoogleAPIError("Google API error")

    # リクエストデータ
    files = ["file1.txt", "file2.txt"]

    # リクエストの送信
    response = client.post("/exercises/request_stream", json=files)

    # レスポンスの検証
    assert response.status_code == 500
    assert response.json() == {
        "detail": "Google APIからエラーが返されました。"
        + "システム管理者に連絡してください。"
    }


# 異常系のテスト - その他の例外
@pytest.mark.asyncio
@patch("app.routers.exercises_stream.generate_content_stream")
async def test_request_content_unexpected_error(
    mock_generate_content_stream: AsyncMock,
) -> None:
    # モックの設定
    mock_generate_content_stream.side_effect = Exception("Unexpected error")

    # リクエストデータ
    files = ["file1.txt", "file2.txt"]

    # リクエストの送信
    response = client.post("/exercises/request_stream", json=files)

    # レスポンスの検証
    assert response.status_code == 500
    assert response.json() == {
        "detail": "コンテンツの生成中に予期せぬエラーが発生しました。"
        + "システム管理者に連絡してください。"
    }
