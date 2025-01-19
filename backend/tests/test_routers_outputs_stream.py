import pytest
from unittest.mock import patch, Mock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.files import File
from datetime import datetime, timezone, timedelta
from typing import Any, AsyncGenerator, Callable, Awaitable
from httpx import AsyncClient, ASGITransport
from google.api_core.exceptions import GoogleAPIError, InvalidArgument, NotFound
from sqlalchemy.exc import SQLAlchemyError
import json
from sqlalchemy import select
from sqlalchemy.sql import text

from app.main import app
from app.models.outputs import Output
from app.models.outputs_files import output_file
from app.models.files import File
from app.routers.outputs_stream import router


# 環境変数を設定するフィクスチャ
@pytest.fixture
def mock_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROJECT_ID", "your_project_id")
    monkeypatch.setenv("REGION", "your_region")


# データベースセッションのクリーンアップを行うフィクスチャ
@pytest.fixture
async def session_cleanup(session: AsyncSession) -> AsyncGenerator:
    yield session
    await session.close()  # セッションをクローズ


# 正常にコンテンツが生成される場合のテスト
@pytest.mark.asyncio
@patch("app.routers.outputs_stream.generate_content_stream")
@patch("app.routers.outputs_stream.get_file_id_by_name_and_userid")
async def test_request_content_stream_success(
    mock_get_file_id: Mock,
    mock_generate_content_stream: Mock,
    mock_env_vars: None,
    session_cleanup: AsyncSession,  # session_cleanupを使って自動クリーンアップ
) -> None:
    # モックファイルを作成してデータベースに挿入
    file_data = File(
        file_name="file1.pdf",
        file_size=1234,
        user_id="test_user",
        created_at=datetime.now(timezone(timedelta(hours=9))),
        updated_at=datetime.now(timezone(timedelta(hours=9))),
    )
    session_cleanup.add(file_data)
    await session_cleanup.commit()
    await session_cleanup.refresh(file_data)

    # モックが返すfile_idを上で挿入したものと一致させる
    mock_get_file_id.return_value = file_data.id

    # モックストリームを返すようにパッチ
    async def mock_streamer(file_names: list[str], style: str) -> AsyncGenerator[str, None]:
        yield "生成されたコンテンツ"

    mock_generate_content_stream.return_value = mock_streamer(["file1.pdf"], "casual")


# ファイルが見つからない場合のテスト
@pytest.mark.asyncio
@patch("app.routers.outputs_stream.get_file_id_by_name_and_userid", return_value=None)
async def test_request_content_stream_file_not_found(mock_get_file_id: Mock) -> None:
    """
    ファイルが見つからない場合のテスト。
    """
    transport = ASGITransport(app=app)  # type: ignore
    headers = {"Authorization": "Bearer fake_token"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/outputs/request_stream",
            json={"files": ["file1.pdf"], "title": "ファイル分析課題", "style": "casual"},
            headers=headers,
        )
    assert response.status_code == 404
    assert "指定されたファイルの一部がデータベースに存在しません" in response.text


# Google Cloud Storageでファイルが見つからない場���のテスト
@pytest.mark.asyncio
@patch("app.routers.outputs_stream.get_file_id_by_name_and_userid")
@patch("app.routers.outputs_stream.generate_content_stream")
async def test_request_content_stream_gcs_not_found(
    mock_generate_content_stream: Mock,
    mock_get_file_id: Mock,
    session_cleanup: AsyncSession,
) -> None:
    """
    Google Cloud Storageでファイルが見つからない場合のテスト
    """
    file_data = File(
        file_name="missing_file.pdf",
        file_size=1234,
        user_id="test_user",
        created_at=datetime.now(timezone(timedelta(hours=9))),
        updated_at=datetime.now(timezone(timedelta(hours=9))),
    )
    session_cleanup.add(file_data)
    await session_cleanup.commit()
    await session_cleanup.refresh(file_data)

    mock_get_file_id.return_value = file_data.id
    mock_generate_content_stream.side_effect = NotFound("Specified file not found in GCS")

    transport = ASGITransport(app=app)  # type: ignore
    headers = {"Authorization": "Bearer fake_token"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/outputs/request_stream",
            json={"files": ["file111111.pdf"], "title": "ファイル分析課題", "style": "casual"},
            headers=headers,
        )

    assert response.status_code == 404
    assert "指定されたファイルがGoogle Cloud Storageに見つかりません" in response.text


# 無効なファイル名形式の場合のテスト
@pytest.mark.asyncio
@patch("app.routers.outputs_stream.get_file_id_by_name_and_userid")
@patch("app.routers.outputs_stream.generate_content_stream")
async def test_request_content_stream_invalid_filename(
    mock_generate_content_stream: Mock,
    mock_get_file_id: Mock,
    session_cleanup: AsyncSession,
) -> None:
    """
    無効なファイル名形式でリクエストした場合のテスト
    """
    file_data = File(
        file_name="invalid/file/name.pdf",
        file_size=1234,
        user_id="test_user",
        created_at=datetime.now(timezone(timedelta(hours=9))),
        updated_at=datetime.now(timezone(timedelta(hours=9))),
    )
    session_cleanup.add(file_data)
    await session_cleanup.commit()
    await session_cleanup.refresh(file_data)

    mock_get_file_id.return_value = file_data.id
    mock_generate_content_stream.side_effect = InvalidArgument("Invalid file name format")

    transport = ASGITransport(app=app)  # type: ignore
    headers = {"Authorization": "Bearer fake_token"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/outputs/request_stream",
            json={"files": ["invalid/file/name.pdf"], "title": "テスト", "style": "casual"},
            headers=headers,
        )

    assert response.status_code == 400
    assert "ファイル名の形式が無効です" in response.text


# Google APIエラーの場合のテスト
@pytest.mark.asyncio
@patch("app.routers.outputs_stream.get_file_id_by_name_and_userid")
@patch("app.routers.outputs_stream.generate_content_stream")
async def test_request_content_stream_google_api_error(
    mock_generate_content_stream: Mock,
    mock_get_file_id: Mock,
    session_cleanup: AsyncSession,
) -> None:
    """
    Google APIがエラーを返した場合のテスト
    """
    file_data = File(
        file_name="file1.pdf",
        file_size=1234,
        user_id="test_user",
        created_at=datetime.now(timezone(timedelta(hours=9))),
        updated_at=datetime.now(timezone(timedelta(hours=9))),
    )
    session_cleanup.add(file_data)
    await session_cleanup.commit()
    await session_cleanup.refresh(file_data)

    mock_get_file_id.return_value = file_data.id
    mock_generate_content_stream.side_effect = GoogleAPIError("Google API error occurred")

    transport = ASGITransport(app=app)  # type: ignore
    headers = {"Authorization": "Bearer fake_token"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/outputs/request_stream",
            json={"files": ["file1.pdf"], "title": "タイトル", "style": "casual"},
            headers=headers,
        )

    assert response.status_code == 500
    assert "Google APIからエラーが返されました" in response.text


# ファイルIDの取得に失敗した場合のテスト
@pytest.mark.asyncio
@patch("app.routers.outputs_stream.get_file_id_by_name_and_userid")
async def test_request_content_stream_file_id_error(
    mock_get_file_id: Mock,
    session_cleanup: AsyncSession,
) -> None:
    """
    ファイルIDの取得時にエラーが発生した場合のテスト
    """
    mock_get_file_id.side_effect = SQLAlchemyError("Database error during file ID retrieval")

    transport = ASGITransport(app=app)  # type: ignore
    headers = {"Authorization": "Bearer fake_token"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/outputs/request_stream",
            json={"files": ["file1.pdf"], "title": "タイトル", "style": "casual"},
            headers=headers,
        )

    assert response.status_code == 500
    assert "データベースからファイル情報を取得する際にエラーが発生しました" in response.text