import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock, Mock
from fastapi import FastAPI
from pytest import MonkeyPatch
from app.routers.outputs_stream import router
from google.api_core.exceptions import GoogleAPIError, InvalidArgument, NotFound
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.main import app


# 環境変数を設定するフィクスチャ
@pytest.fixture
def mock_env_vars(monkeypatch: MonkeyPatch) -> None:
    """
    環境変数を設定するフィクスチャ

    :param monkeypatch: pytestのMonkeyPatchオブジェクト
    :type monkeypatch: MonkeyPatch
    """
    # 環境変数を設定
    monkeypatch.setenv("PROJECT_ID", "your_project_id")
    monkeypatch.setenv("REGION", "your_region")


# sessionフィクスチャを提供するフィクスチャを定義
@pytest.fixture
async def session(
    setup_and_teardown_database: AsyncGenerator[AsyncSession, None],
) -> AsyncGenerator[AsyncSession, None]:
    """
    データベースのセットアップとテアダウンを行うフィクスチャ

    :param setup_and_teardown_database: データベースのセットアップとテアダウンを行う非同期ジェネレータ
    :type setup_and_teardown_database: AsyncGenerator[AsyncSession, None]
    :yield: 非同期セッション
    :rtype: AsyncGenerator[AsyncSession, None]
    """
    async with setup_and_teardown_database as session:  # type: ignore
        yield session


# モックのコンテンツ
class MockContent:
    def to_dict(self) -> dict:
        """
        モックのコンテンツを辞書形式で返す

        :return: モックのコンテンツ
        :rtype: dict
        """
        return {
            "candidates": [{"content": {"parts": [{"text": "生成されたコンテンツ"}]}}]
        }


# 正常にコンテンツが生成される場合のテスト
@pytest.mark.asyncio
@patch("app.routers.outputs_stream.generate_content_stream")
async def test_request_content_stream_success(
    mock_generate_content_stream: Mock, mock_env_vars: None, session: AsyncSession
) -> None:
    """
    正常にコンテンツが生成される場合のテスト

    :param mock_generate_content_stream: モックされたgenerate_content_stream関数
    :type mock_generate_content_stream: Mock
    :param mock_env_vars: 環境変数を設定するフィクスチャ
    :type mock_env_vars: None
    :param session: 非同期セッション
    :type session: AsyncSession
    """
    # フィクスチャを適用
    mock_env_vars

    async def mock_streamer(file_names: list[str]) -> AsyncGenerator[MockContent, None]:
        assert file_names == ["file1.pdf", "file2.pdf"]
        yield MockContent()

    mock_generate_content_stream.return_value = mock_streamer(
        ["file1.pdf", "file2.pdf"]
    )

    transport = ASGITransport(app=app)  # type: ignore
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/outputs/request_stream", json=["file1.pdf", "file2.pdf"]
        )

    assert response.status_code == 200
    content = [chunk async for chunk in response.aiter_text()]
    assert content == ["生成されたコンテンツ"]


# 指定されたファイルが見つからない場合のテスト
@pytest.mark.asyncio
@patch("app.routers.outputs_stream.generate_content_stream")
async def test_request_content_stream_file_not_found(
    mock_generate_content_stream: Mock, mock_env_vars: None
) -> None:
    """
    指定されたファイルが見つからない場合のテスト

    :param mock_generate_content_stream: モックされたgenerate_content_stream関数
    :type mock_generate_content_stream: Mock
    :param mock_env_vars: 環境変数を設定するフィクスチャ
    :type mock_env_vars: None
    """
    # フィクスチャを適用
    mock_env_vars
    mock_generate_content_stream.side_effect = NotFound("File not found")

    transport = ASGITransport(app=app)  # type: ignore
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/outputs/request_stream", json=["non_existent_file.pdf"]
        )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "指定されたファイルがGoogle Cloud Storageに見つかりません。"
        + "ファイル名を再確認してください。"
    }


# 無効なファイル形式が指定された場合のテスト
@pytest.mark.asyncio
@patch("app.routers.outputs_stream.generate_content_stream")
async def test_request_content_stream_invalid_argument(
    mock_generate_content_stream: Mock, mock_env_vars: None
) -> None:
    """
    無効なファイル形式が指定された場合のテスト

    :param mock_generate_content_stream: モックされたgenerate_content_stream関数
    :type mock_generate_content_stream: Mock
    :param mock_env_vars: 環境変数を設定するフィクスチャ
    :type mock_env_vars: None
    """
    # フィクスチャを適用
    mock_env_vars
    mock_generate_content_stream.side_effect = InvalidArgument("Invalid file format")

    transport = ASGITransport(app=app)  # type: ignore
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/outputs/request_stream", json=["invalid_format.txt"])

    assert response.status_code == 400
    assert response.json() == {
        "detail": "ファイル名の形式が無効です。有効なファイル名を指定してください。"
    }


# Google APIエラーが発生した場合のテスト
@pytest.mark.asyncio
@patch("app.routers.outputs_stream.generate_content_stream")
async def test_request_content_stream_google_api_error(
    mock_generate_content_stream: Mock, mock_env_vars: None
) -> None:
    """
    Google APIエラーが発生した場合のテスト

    :param mock_generate_content_stream: モックされたgenerate_content_stream関数
    :type mock_generate_content_stream: Mock
    :param mock_env_vars: 環境変数を設定するフィクスチャ
    :type mock_env_vars: None
    """
    # フィクスチャを適用
    mock_env_vars
    mock_generate_content_stream.side_effect = GoogleAPIError("Google API error")

    transport = ASGITransport(app=app)  # type: ignore
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/outputs/request_stream", json=["file1.pdf", "file2.pdf"]
        )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Google APIからエラーが返されました。"
        + "システム管理者に連絡してください。"
    }


# 予期せぬエラーが発生した場合のテスト
@pytest.mark.asyncio
@patch("app.routers.outputs_stream.generate_content_stream")
async def test_request_content_stream_unexpected_error(
    mock_generate_content_stream: Mock, mock_env_vars: None
) -> None:
    """
    予期せぬエラーが発生した場合のテスト

    :param mock_generate_content_stream: モックされたgenerate_content_stream関数
    :type mock_generate_content_stream: Mock
    :param mock_env_vars: 環境変数を設定するフィクスチャ
    :type mock_env_vars: None
    """
    # フィクスチャを適用
    mock_env_vars
    mock_generate_content_stream.side_effect = Exception("Unexpected error")

    transport = ASGITransport(app=app)  # type: ignore
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/outputs/request_stream", json=["file1.pdf", "file2.pdf"]
        )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "コンテンツの生成中に予期せぬエラーが発生しました。"
        + "システム管理者に連絡してください。"
    }


# 最終的なコンテンツが結合されてログに記録されることを確認するテスト
@pytest.mark.asyncio
@patch("app.routers.outputs_stream.generate_content_stream")
async def test_request_content_stream_final_content_logging(
    mock_generate_content_stream: Mock,
    mock_env_vars: None,
    caplog: pytest.LogCaptureFixture,
    session: AsyncSession,
) -> None:
    """
    最終的なコンテンツが結合されてログに記録されることを確認するテスト

    :param mock_generate_content_stream: モックされたgenerate_content_stream関数
    :type mock_generate_content_stream: Mock
    :param mock_env_vars: 環境変数を設定するフィクスチャ
    :type mock_env_vars: None
    :param caplog: ログキャプチャフィクスチャ
    :type caplog: pytest.LogCaptureFixture
    :param session: 非同期セッション
    :type session: AsyncSession
    """
    # フィクスチャを適用
    mock_env_vars

    async def mock_streamer(file_names: list[str]) -> AsyncGenerator[MockContent, None]:
        yield MockContent()

    mock_generate_content_stream.return_value = mock_streamer(
        ["file1.pdf", "file2.pdf"]
    )

    with caplog.at_level(logging.INFO):
        transport = ASGITransport(app=app)  # type: ignore
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(
                "/outputs/request_stream", json=["file1.pdf", "file2.pdf"]
            )

        assert response.status_code == 200
        content = [chunk async for chunk in response.aiter_text()]
        assert content == ["生成されたコンテンツ"]
        # 最後のログメッセージを確認
        assert "Final content for DB: 生成されたコンテンツ" in caplog.text
