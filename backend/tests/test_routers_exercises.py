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
from app.models.exercises import Exercise
from app.models.exercises_files import exercise_file
from app.models.files import File
from app.routers.exercises import request_choice_question_json


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
@patch("app.routers.exercises.generate_content_stream")
@patch("app.routers.exercises.get_file_id_by_name_and_userid")
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
    )
    session_cleanup.add(file_data)
    await session_cleanup.commit()
    await session_cleanup.refresh(file_data)

    # モックが返すfile_idを上で挿入したものと一致させる
    mock_get_file_id.return_value = file_data.id

    # モックストリームを返すようにパッチ
    async def mock_streamer(file_names: list[str]) -> AsyncGenerator[str, None]:
        yield "生成されたコンテンツ"

    mock_generate_content_stream.return_value = mock_streamer(["file1.pdf", "file2.pdf"])


# ファイルが見つからない場合のテスト
@pytest.mark.asyncio
@patch("app.routers.exercises.get_file_id_by_name_and_userid", return_value=None)
async def test_request_content_stream_file_not_found(mock_get_file_id: Mock) -> None:
    """
    ファイルが見つからない場合のテスト。
    """
    transport = ASGITransport(app=app)  # type: ignore
    headers = {"Authorization": "Bearer fake_token"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/exercises/request_stream",
            json={"files": ["file1.pdf"], "title": "ファイル分析課題"},
            headers=headers,
        )
    assert response.status_code == 404
    assert "指定されたファイルの一部がデータベースに存在しません" in response.text


# Google Cloud Storageでファイルが見つからない場合のテスト
@pytest.mark.asyncio
@patch("app.routers.exercises.get_file_id_by_name_and_userid")
@patch("app.routers.exercises.generate_content_stream")
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
            "/exercises/request_stream",
            json={"files": ["file111111.pdf"], "title": "ファイル分析課題"},
            headers=headers,
        )

    assert response.status_code == 404
    assert "指定されたファイルがGoogle Cloud Storageに見つかりません" in response.text


# 無効なファイル名形式の場合のテスト
@pytest.mark.asyncio
@patch("app.routers.exercises.get_file_id_by_name_and_userid")
@patch("app.routers.exercises.generate_content_stream")
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
            "/exercises/request_stream",
            json={"files": ["invalid/file/name.pdf"], "title": "テスト"},
            headers=headers,
        )

    assert response.status_code == 400
    assert "ファイル名の形式が無効です" in response.text


# Google APIエラーの場合のテスト
@pytest.mark.asyncio
@patch("app.routers.exercises.get_file_id_by_name_and_userid")
@patch("app.routers.exercises.generate_content_stream")
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
            "/exercises/request_stream",
            json={"files": ["file1.pdf"], "title": "タイトル"},
            headers=headers,
        )

    assert response.status_code == 500
    assert "Google APIからエラーが返されました" in response.text


# ファイルIDの取得に失敗した場合のテスト
@pytest.mark.asyncio
@patch("app.routers.exercises.get_file_id_by_name_and_userid")
async def test_request_content_stream_file_id_error(
    mock_get_file_id: Mock,
) -> None:
    """
    ファイルIDの取得時にエラーが発生した場合のテスト
    """
    mock_get_file_id.side_effect = SQLAlchemyError("Database error during file ID retrieval")

    transport = ASGITransport(app=app)  # type: ignore
    headers = {"Authorization": "Bearer fake_token"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/exercises/request_stream",
            json={"files": ["file1.pdf"], "title": "タイトル"},
            headers=headers,
        )

    assert response.status_code == 500
    assert "データベースからファイル情報を取得する際にエラーが発生しました" in response.text


# 選択問題生成の正常系テスト
@pytest.mark.asyncio
@patch("app.routers.exercises.generate_content_json")
@patch("app.routers.exercises.get_file_id_by_name_and_userid")
async def test_multiple_choice_success(
    mock_get_file_id: Mock,
    mock_generate_content_json: Mock,
    session_cleanup: AsyncSession,
) -> None:
    """
    選択問題生成の正常系テスト
    """
    # テスト用のファイルデータを作成
    file_data = File(
        file_name="test_file.pdf",
        file_size=1234,
        user_id="test_user",
        created_at=datetime.now(timezone(timedelta(hours=9))),
    )
    session_cleanup.add(file_data)
    await session_cleanup.commit()
    await session_cleanup.refresh(file_data)

    # モックの設定
    mock_get_file_id.return_value = file_data.id
    mock_response = {
        "question": "テスト問題",
        "choices": ["選択肢1", "選択肢2", "選択肢3", "選択肢4"],
        "correct_answer": 0,
    }
    mock_generate_content_json.return_value = mock_response

    # リクエストの実行
    transport = ASGITransport(app=app)  # type: ignore
    headers = {"Authorization": "Bearer fake_token"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/exercises/multiple_choice",
            json={"files": ["test_file.pdf"], "title": "タイトル"},
            headers=headers,
        )

    # アサーション
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["question"] == "テスト問題"
    assert len(response_data["choices"]) == 4
    assert isinstance(response_data["correct_answer"], int)

    # 新しいセッションでデータベースの状態を確認
    await session_cleanup.commit()

    # データベースに保存されていることを確認
    stmt = select(Exercise).where(
        Exercise.user_id == "test_user", Exercise.exercise_type == "multiple_choice"
    )
    result = await session_cleanup.execute(stmt)
    exercise = result.scalar_one_or_none()
    assert exercise is not None
    assert exercise.exercise_type == "multiple_choice"
    assert json.loads(str(exercise.response))["question"] == "テスト問題"


# 練習問題一覧取得の正常系テスト
@pytest.mark.asyncio
async def test_list_exercises_success(
    session_cleanup: AsyncSession,
) -> None:
    """
    練習問題一覧取得の正常系テスト
    """
    # テストデータの作成
    exercises = []
    for i in range(3):
        exercise = Exercise(
            title=f"test_title_{i}",
            response=json.dumps({"test": f"response_{i}"}),
            user_id="test_user",
            created_at=datetime.now(timezone(timedelta(hours=9))),
            exercise_type="multiple_choice",
        )
        exercises.append(exercise)
        session_cleanup.add(exercise)

    await session_cleanup.commit()
    for exercise in exercises:
        await session_cleanup.refresh(exercise)

    # リクエストの実行
    transport = ASGITransport(app=app)  # type: ignore
    headers = {"Authorization": "Bearer fake_token"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/exercises/list", headers=headers)

    # アサーション
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 3
    for exercise in response_data:
        assert "id" in exercise
        assert "title" in exercise
        assert "response" in exercise
        assert "user_id" in exercise
        assert "created_at" in exercise
        assert "exercise_type" in exercise


# 特定の練習問題取得の正常系テスト
@pytest.mark.asyncio
async def test_get_exercise_success(
    session_cleanup: AsyncSession,
) -> None:
    """
    特定の練習問題取得の正常系テスト
    """
    # テストデータの作成
    exercise = Exercise(
        title="test_title",
        response=json.dumps({"test": "response"}),
        user_id="test_user",
        created_at=datetime.now(timezone(timedelta(hours=9))),
        exercise_type="multiple_choice",
    )
    session_cleanup.add(exercise)
    await session_cleanup.commit()
    await session_cleanup.refresh(exercise)

    # リクエストの実行
    transport = ASGITransport(app=app)  # type: ignore
    headers = {"Authorization": "Bearer fake_token"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/exercises/{exercise.id}", headers=headers)

    # アサーション
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == exercise.id
    assert response_data["user_id"] == "test_user"
    assert response_data["exercise_type"] == "multiple_choice"
    assert response_data["title"] == "test_title"


# 選択問題削除の正常系テスト
@pytest.mark.asyncio
async def test_delete_exercise_success(
    session_cleanup: AsyncSession,
) -> None:
    """
    練習問題削除の正常系テスト
    """
    # テストデータの作成
    exercise = Exercise(
        title="test_title",
        response=json.dumps({"test": "response"}),
        user_id="test_user",
        created_at=datetime.now(timezone(timedelta(hours=9))),
        exercise_type="multiple_choice",
    )
    session_cleanup.add(exercise)
    await session_cleanup.commit()
    await session_cleanup.refresh(exercise)

    exercise_id = exercise.id

    # リクエストの実行
    transport = ASGITransport(app=app)  # type: ignore
    headers = {"Authorization": "Bearer fake_token"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete(f"/exercises/{exercise_id}", headers=headers)

    # アサーション
    assert response.status_code == 200

    # 新しいトランザクションで削除を確認
    await session_cleanup.commit()

    # データベースから削除されていることを確認
    stmt = select(Exercise).where(Exercise.id == exercise_id)
    result = await session_cleanup.execute(stmt)
    deleted_exercise = result.scalar_one_or_none()
    assert deleted_exercise is None
