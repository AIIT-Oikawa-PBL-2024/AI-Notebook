import pytest
from datetime import datetime
from unittest.mock import AsyncMock, Mock, call
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.exc import SQLAlchemyError

from app.models.answers import Answer
from app.schemas.answers import (
    SaveAnswerPayload,
    ResponseData,
    Choice,
    AnswerResponse,
    DeleteAnswersResult,
)
from app.cruds.answers import (
    save_answers_to_db,
    get_answers_by_user,
    delete_answer_by_user,
    delete_answers_by_user,
)


@pytest.fixture
def mock_db() -> AsyncMock:
    """AsyncSessionのモックを作成するフィクスチャ"""
    mock = AsyncMock(spec=AsyncSession)
    mock.commit = AsyncMock()
    mock.rollback = AsyncMock()
    mock.add_all = Mock()
    mock.delete = AsyncMock()
    return mock


@pytest.fixture
def sample_datetime() -> datetime:
    """テスト用の固定日時を返すフィクスチャ"""
    return datetime(2024, 1, 1, 12, 0, 0)


@pytest.fixture
def sample_response_data() -> ResponseData:
    """ResponseDataスキーマのサンプルデータを作成するフィクスチャ"""
    return ResponseData(
        question_id="q1",
        question_text="What is 2+2?",
        choices=Choice(
            choice_a="3",
            choice_b="4",
            choice_c="5",
            choice_d="6",
        ),
        user_selected_choice="choice_b",
        correct_choice="choice_b",
        is_correct=True,
        explanation="2+2 is 4.",
    )


@pytest.fixture
def sample_save_answer_payload(sample_response_data: ResponseData) -> SaveAnswerPayload:
    """SaveAnswerPayloadスキーマのサンプルデータを作成するフィクスチャ"""
    return SaveAnswerPayload(
        title="Sample Quiz",
        relatedFiles=["file1.png", "file2.jpg"],
        responses=[sample_response_data, sample_response_data],  # 複数の回答を含む
    )


@pytest.fixture
def sample_answer(sample_datetime: datetime) -> Answer:
    """Answerモデルのサンプルデータを作成するフィクスチャ"""
    return Answer(
        id=1,
        title="Sample Quiz",
        related_files=["file1.png", "file2.jpg"],
        question_id="q1",
        question_text="What is 2+2?",
        choice_a="3",
        choice_b="4",
        choice_c="5",
        choice_d="6",
        user_selected_choice="choice_b",
        correct_choice="choice_b",
        is_correct=True,
        explanation="2+2 is 4.",
        user_id="test-user-123",
        created_at=sample_datetime,
        updated_at=sample_datetime,
    )


@pytest.fixture
def sample_delete_answers_result() -> DeleteAnswersResult:
    """DeleteAnswersResultスキーマのサンプルデータを作成するフィクスチャ"""
    return DeleteAnswersResult(
        deleted_ids=[1, 2],
        not_found_ids=[3],
        unauthorized_ids=[4],
    )


@pytest.mark.asyncio
async def test_save_answers_to_db_success(
    mock_db: AsyncMock,
    sample_save_answer_payload: SaveAnswerPayload,
    sample_datetime: datetime,
) -> None:
    """save_answers_to_db関数の正常系テスト"""
    user_id = "test-user-123"

    # テスト実行
    await save_answers_to_db(mock_db, sample_save_answer_payload, user_id, sample_datetime)

    # アサーション
    assert mock_db.add_all.called
    added_answers = mock_db.add_all.call_args[0][0]
    assert len(added_answers) == len(sample_save_answer_payload.responses)
    for answer, response in zip(added_answers, sample_save_answer_payload.responses):
        assert answer.title == sample_save_answer_payload.title
        assert answer.related_files == sample_save_answer_payload.relatedFiles
        assert answer.question_id == response.question_id
        assert answer.question_text == response.question_text
        assert answer.choice_a == response.choices.choice_a
        assert answer.choice_b == response.choices.choice_b
        assert answer.choice_c == response.choices.choice_c
        assert answer.choice_d == response.choices.choice_d
        assert answer.user_selected_choice == response.user_selected_choice
        assert answer.correct_choice == response.correct_choice
        assert answer.is_correct == response.is_correct
        assert answer.explanation == response.explanation
        assert answer.user_id == user_id
        assert answer.created_at == sample_datetime
        assert answer.updated_at == sample_datetime
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_save_answers_to_db_db_error(
    mock_db: AsyncMock,
    sample_save_answer_payload: SaveAnswerPayload,
    sample_datetime: datetime,
) -> None:
    """save_answers_to_db関数のデータベースエラー系テスト"""
    user_id = "test-user-123"
    mock_db.commit.side_effect = SQLAlchemyError("Commit failed")

    with pytest.raises(SQLAlchemyError):
        await save_answers_to_db(mock_db, sample_save_answer_payload, user_id, sample_datetime)

    # アサーション
    assert mock_db.rollback.called
    assert mock_db.add_all.called


@pytest.mark.asyncio
async def test_save_answers_to_db_unexpected_error(
    mock_db: AsyncMock,
    sample_save_answer_payload: SaveAnswerPayload,
    sample_datetime: datetime,
) -> None:
    """save_answers_to_db関数の予期しないエラー系テスト"""
    user_id = "test-user-123"
    mock_db.add_all.side_effect = Exception("Unexpected error")

    with pytest.raises(Exception, match="Unexpected error"):
        await save_answers_to_db(mock_db, sample_save_answer_payload, user_id, sample_datetime)

    # アサーション
    assert mock_db.rollback.called


@pytest.mark.asyncio
async def test_get_answers_by_user_success(
    mock_db: AsyncMock,
    sample_answer: Answer,
) -> None:
    """get_answers_by_user関数の正常系テスト"""
    user_id = "test-user-123"
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = [sample_answer]
    mock_db.execute.return_value = mock_result

    # テスト実行
    result = await get_answers_by_user(mock_db, user_id)

    # アサーション
    assert len(result) == 1
    answer_response = result[0]
    assert isinstance(answer_response, AnswerResponse)
    assert answer_response.id == sample_answer.id
    assert answer_response.title == sample_answer.title
    assert answer_response.related_files == sample_answer.related_files
    assert answer_response.question_id == sample_answer.question_id
    assert answer_response.question_text == sample_answer.question_text
    assert answer_response.choice_a == sample_answer.choice_a
    assert answer_response.choice_b == sample_answer.choice_b
    assert answer_response.choice_c == sample_answer.choice_c
    assert answer_response.choice_d == sample_answer.choice_d
    assert answer_response.user_selected_choice == sample_answer.user_selected_choice
    assert answer_response.correct_choice == sample_answer.correct_choice
    assert answer_response.is_correct == sample_answer.is_correct
    assert answer_response.explanation == sample_answer.explanation
    assert answer_response.user_id == sample_answer.user_id
    assert answer_response.created_at == sample_answer.created_at
    assert answer_response.updated_at == sample_answer.updated_at


@pytest.mark.asyncio
async def test_get_answers_by_user_db_error(
    mock_db: AsyncMock,
) -> None:
    """get_answers_by_user関数のデータベースエラー系テスト"""
    user_id = "test-user-123"
    mock_db.execute.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(SQLAlchemyError):
        await get_answers_by_user(mock_db, user_id)


@pytest.mark.asyncio
async def test_get_answers_by_user_unexpected_error(
    mock_db: AsyncMock,
) -> None:
    """get_answers_by_user関数の予期しないエラー系テスト"""
    user_id = "test-user-123"
    mock_db.execute.side_effect = Exception("Unexpected error")

    with pytest.raises(Exception):
        await get_answers_by_user(mock_db, user_id)


@pytest.mark.asyncio
async def test_delete_answer_by_user_success(
    mock_db: AsyncMock,
    sample_answer: Answer,
) -> None:
    """delete_answer_by_user関数の正常系テスト"""
    user_id = "test-user-123"

    # テスト実行
    await delete_answer_by_user(mock_db, sample_answer, user_id)

    # アサーション
    mock_db.delete.assert_called_once_with(sample_answer)
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_answer_by_user_unauthorized(
    mock_db: AsyncMock,
    sample_answer: Answer,
) -> None:
    """delete_answer_by_user関数の権限エラーテスト"""
    user_id = "different-user"

    with pytest.raises(ValueError, match="User is not authorized to delete this answer"):
        await delete_answer_by_user(mock_db, sample_answer, user_id)

    # アサーション
    mock_db.delete.assert_not_called()
    mock_db.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete_answer_by_user_db_error(
    mock_db: AsyncMock,
    sample_answer: Answer,
) -> None:
    """delete_answer_by_user関数のデータベースエラー系テスト"""
    user_id = "test-user-123"
    mock_db.delete.side_effect = SQLAlchemyError("Delete failed")

    with pytest.raises(SQLAlchemyError):
        await delete_answer_by_user(mock_db, sample_answer, user_id)

    # アサーション
    mock_db.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_delete_answers_by_user_success(
    mock_db: AsyncMock,
    sample_datetime: datetime,
) -> None:
    """delete_answers_by_user関数の正常系テスト"""
    user_id = "test-user-123"
    answer_ids = [1, 2, 3, 4]
    owned_answers = [
        Answer(
            id=1,
            user_id=user_id,
            created_at=sample_datetime,
            title="",
            related_files=[],
            question_id="",
            question_text="",
            choice_a="",
            choice_b="",
            choice_c="",
            choice_d="",
            user_selected_choice="",
            correct_choice="",
            is_correct=True,
            explanation="",
            updated_at=sample_datetime,
        ),
        Answer(
            id=2,
            user_id=user_id,
            created_at=sample_datetime,
            title="",
            related_files=[],
            question_id="",
            question_text="",
            choice_a="",
            choice_b="",
            choice_c="",
            choice_d="",
            user_selected_choice="",
            correct_choice="",
            is_correct=True,
            explanation="",
            updated_at=sample_datetime,
        ),
    ]
    unauthorized_answers = [
        Answer(
            id=4,
            user_id="other-user",
            created_at=sample_datetime,
            title="",
            related_files=[],
            question_id="",
            question_text="",
            choice_a="",
            choice_b="",
            choice_c="",
            choice_d="",
            user_selected_choice="",
            correct_choice="",
            is_correct=True,
            explanation="",
            updated_at=sample_datetime,
        ),
    ]
    # モックの設定
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = owned_answers + unauthorized_answers
    mock_db.execute.return_value = mock_result

    # テスト実行
    result = await delete_answers_by_user(mock_db, answer_ids, user_id)

    # アサーション
    expected_deleted_ids = [1, 2]
    expected_not_found_ids = [3]
    expected_unauthorized_ids = [4]
    assert result.deleted_ids == expected_deleted_ids
    assert result.not_found_ids == expected_not_found_ids
    assert result.unauthorized_ids == expected_unauthorized_ids

    # 削除が正しく呼ばれていること
    expected_calls = [call(answer) for answer in owned_answers]
    mock_db.delete.assert_has_calls(expected_calls, any_order=True)
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_delete_answers_by_user_partial_ownership(
    mock_db: AsyncMock,
    sample_datetime: datetime,
) -> None:
    """delete_answers_by_user関数の一部の回答が所有者でない場合のテスト"""
    user_id = "test-user-123"
    answer_ids = [1, 2]
    owned_answers = [
        Answer(
            id=1,
            user_id=user_id,
            created_at=sample_datetime,
            title="",
            related_files=[],
            question_id="",
            question_text="",
            choice_a="",
            choice_b="",
            choice_c="",
            choice_d="",
            user_selected_choice="",
            correct_choice="",
            is_correct=True,
            explanation="",
            updated_at=sample_datetime,
        ),
    ]
    unauthorized_answers = [
        Answer(
            id=2,
            user_id="other-user",
            created_at=sample_datetime,
            title="",
            related_files=[],
            question_id="",
            question_text="",
            choice_a="",
            choice_b="",
            choice_c="",
            choice_d="",
            user_selected_choice="",
            correct_choice="",
            is_correct=True,
            explanation="",
            updated_at=sample_datetime,
        ),
    ]
    # モックの設定
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = owned_answers + unauthorized_answers
    mock_db.execute.return_value = mock_result

    # テスト実行
    result = await delete_answers_by_user(mock_db, answer_ids, user_id)

    # アサーション
    expected_deleted_ids: List[int] = [1]
    expected_not_found_ids: List[int] = []
    expected_unauthorized_ids: List[int] = [2]
    assert result.deleted_ids == expected_deleted_ids
    assert result.not_found_ids == expected_not_found_ids
    assert result.unauthorized_ids == expected_unauthorized_ids

    # 削除が正しく呼ばれていること
    mock_db.delete.assert_called_once_with(owned_answers[0])
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_delete_answers_by_user_not_found(
    mock_db: AsyncMock,
    sample_datetime: datetime,
) -> None:
    """delete_answers_by_user関数の存在しない回答IDが含まれる場合のテスト"""
    user_id = "test-user-123"
    answer_ids = [1, 2, 3]
    existing_answers = [
        Answer(
            id=1,
            user_id=user_id,
            created_at=sample_datetime,
            title="",
            related_files=[],
            question_id="",
            question_text="",
            choice_a="",
            choice_b="",
            choice_c="",
            choice_d="",
            user_selected_choice="",
            correct_choice="",
            is_correct=True,
            explanation="",
            updated_at=sample_datetime,
        ),
    ]
    # モックの設定
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = existing_answers
    mock_db.execute.return_value = mock_result

    # テスト実行
    result = await delete_answers_by_user(mock_db, answer_ids, user_id)

    # アサーション
    expected_deleted_ids = [1]
    expected_not_found_ids = [2, 3]
    expected_unauthorized_ids: List[int] = []
    assert result.deleted_ids == expected_deleted_ids
    assert result.not_found_ids == expected_not_found_ids
    assert result.unauthorized_ids == expected_unauthorized_ids

    # 削除が正しく呼ばれていること
    mock_db.delete.assert_called_once_with(existing_answers[0])
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_delete_answers_by_user_db_error(
    mock_db: AsyncMock,
    sample_datetime: datetime,
) -> None:
    """delete_answers_by_user関数のデータベースエラー系テスト"""
    user_id = "test-user-123"
    answer_ids = [1]
    owned_answers = [
        Answer(
            id=1,
            user_id=user_id,
            created_at=sample_datetime,
            title="",
            related_files=[],
            question_id="",
            question_text="",
            choice_a="",
            choice_b="",
            choice_c="",
            choice_d="",
            user_selected_choice="",
            correct_choice="",
            is_correct=True,
            explanation="",
            updated_at=sample_datetime,
        ),
    ]
    # モックの設定
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = owned_answers
    mock_db.execute.return_value = mock_result
    mock_db.delete.side_effect = SQLAlchemyError("Delete failed")

    with pytest.raises(SQLAlchemyError):
        await delete_answers_by_user(mock_db, answer_ids, user_id)

    # アサーション
    mock_db.rollback.assert_called_once()
