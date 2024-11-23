import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

import app.models.exercises as exercises_models
import app.models.files as files_models
import app.schemas.exercises as exercises_schemas
from app.cruds.exercises import (
    create_exercise,
    get_exercises_by_user,
    get_exercise_by_id_and_user,
    delete_exercise_by_user,
    get_exercise_files_by_user,
)


@pytest.fixture
def mock_db() -> AsyncMock:
    """AsyncSessionのモックを作成するフィクスチャ"""
    mock = AsyncMock(spec=AsyncSession)
    mock.commit = AsyncMock()
    mock.rollback = AsyncMock()
    mock.refresh = AsyncMock()
    mock.flush = AsyncMock()
    return mock


@pytest.fixture
def sample_datetime() -> datetime:
    """テスト用の固定日時を返すフィクスチャ"""
    return datetime(2024, 1, 1, 12, 0, 0)


@pytest.fixture
def sample_exercise_create(sample_datetime: datetime) -> exercises_schemas.ExerciseCreate:
    """ExerciseCreateスキーマのサンプルデータを作成するフィクスチャ"""
    return exercises_schemas.ExerciseCreate(
        user_id="test-user-123",
        response="def add(a, b):\n    return a + b",
        exercise_type="python",
        created_at=sample_datetime,
        file_names=["test1.py", "test2.py"],
        title="サンプル練習問題",  # タイトルを追加
    )


@pytest.fixture
def sample_exercise(sample_datetime: datetime) -> exercises_models.Exercise:
    """Exerciseモデルのサンプルデータを作成するフィクスチャ"""
    return exercises_models.Exercise(
        id=1,
        user_id="test-user-123",
        response="def add(a, b):\n    return a + b",
        exercise_type="python",
        created_at=sample_datetime,
        title="サンプル練習問題",  # タイトルを追加
    )


@pytest.fixture
def sample_files(sample_datetime: datetime) -> list[files_models.File]:
    """Fileモデルのサンプルデータを作成するフィクスチャ"""
    return [
        files_models.File(
            id=1,
            file_name="test1.py",
            file_size=100,
            user_id="test-user-123",
            created_at=sample_datetime,
        ),
        files_models.File(
            id=2,
            file_name="test2.py",
            file_size=200,
            user_id="test-user-123",
            created_at=sample_datetime,
        ),
    ]


@pytest.mark.asyncio
async def test_create_exercise_success(
    mock_db: AsyncMock,
    sample_exercise_create: exercises_schemas.ExerciseCreate,
    sample_files: list[files_models.File],
) -> None:
    """create_exercise関数の正常系テスト"""
    # モックの設定
    mock_db.execute = AsyncMock(return_value=Mock(scalars=lambda: Mock(all=lambda: sample_files)))

    # テスト実行
    result = await create_exercise(mock_db, sample_exercise_create)

    # アサーション
    assert result is not None
    assert mock_db.add.called
    assert mock_db.commit.called
    assert mock_db.refresh.called
    assert result.response == sample_exercise_create.response
    assert result.user_id == sample_exercise_create.user_id
    assert result.exercise_type == sample_exercise_create.exercise_type
    assert result.title == sample_exercise_create.title  # タイトルの検証を追加


@pytest.mark.asyncio
async def test_get_exercises_by_user_success(
    mock_db: AsyncMock, sample_exercise: exercises_models.Exercise
) -> None:
    """get_exercises_by_user関数の正常系テスト"""
    # モックの設定
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = [sample_exercise]
    mock_db.execute.return_value = mock_result

    # テスト実行
    result = await get_exercises_by_user(mock_db, "test-user-123")

    # アサーション
    assert len(result) == 1
    exercise_read = result[0]
    assert isinstance(exercise_read, exercises_schemas.ExerciseRead)
    assert exercise_read.id == sample_exercise.id
    assert exercise_read.response == sample_exercise.response
    assert exercise_read.user_id == sample_exercise.user_id
    assert exercise_read.exercise_type == sample_exercise.exercise_type
    assert exercise_read.created_at == sample_exercise.created_at
    assert exercise_read.title == sample_exercise.title  # タイトルの検証を追加


@pytest.mark.asyncio
async def test_get_exercises_by_user_db_error(mock_db: AsyncMock) -> None:
    """get_exercises_by_user関数のエラー系テスト"""
    # モックの設定
    mock_db.execute.side_effect = SQLAlchemyError("Database error")

    # テスト実行とアサーション
    with pytest.raises(SQLAlchemyError):
        await get_exercises_by_user(mock_db, "test-user-123")


@pytest.mark.asyncio
async def test_get_exercise_by_id_and_user_success(
    mock_db: AsyncMock, sample_exercise: exercises_models.Exercise
) -> None:
    """get_exercise_by_id_and_user関数の正常系テスト"""
    # モックの設定
    mock_result = Mock()
    mock_result.scalars.return_value.first.return_value = sample_exercise
    mock_db.execute.return_value = mock_result

    # テスト実行
    result = await get_exercise_by_id_and_user(mock_db, 1, "test-user-123")

    # アサーション
    assert result is not None
    assert result.id == sample_exercise.id
    assert result.response == sample_exercise.response
    assert result.user_id == sample_exercise.user_id
    assert result.exercise_type == sample_exercise.exercise_type


@pytest.mark.asyncio
async def test_delete_exercise_by_user_success(
    mock_db: AsyncMock, sample_exercise: exercises_models.Exercise
) -> None:
    """delete_exercise_by_user関数の正常系テスト"""
    # テスト実行
    await delete_exercise_by_user(mock_db, sample_exercise, "test-user-123")

    # アサーション
    mock_db.delete.assert_called_once_with(sample_exercise)
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_exercise_by_user_unauthorized(
    mock_db: AsyncMock, sample_exercise: exercises_models.Exercise
) -> None:
    """delete_exercise_by_user関数の権限エラーテスト"""
    # テスト実行とアサーション
    with pytest.raises(ValueError, match="User is not authorized to delete this exercise"):
        await delete_exercise_by_user(mock_db, sample_exercise, "different-user")


@pytest.mark.asyncio
async def test_get_exercise_files_by_user_success(
    mock_db: AsyncMock,
    sample_exercise: exercises_models.Exercise,
    sample_files: list[files_models.File],
) -> None:
    """get_exercise_files_by_user関数の正常系テスト"""
    # モックの設定
    sample_exercise.files = sample_files
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = sample_exercise
    mock_db.execute.return_value = mock_result

    # テスト実行
    result = await get_exercise_files_by_user(mock_db, 1, "test-user-123")

    # アサーション
    assert len(result) == 2
    assert result == sample_files
    assert result[0].file_name == "test1.py"
    assert result[1].file_name == "test2.py"


@pytest.mark.asyncio
async def test_get_exercise_files_by_user_not_found(mock_db: AsyncMock) -> None:
    """get_exercise_files_by_user関数の存在しない練習問題テスト"""
    # モックの設定
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    # テスト実行とアサーション
    with pytest.raises(ValueError, match="Exercise with ID 1 not found for user test-user-123"):
        await get_exercise_files_by_user(mock_db, 1, "test-user-123")
