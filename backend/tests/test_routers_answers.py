import pytest
import json
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import AsyncGenerator
from app.main import app
from app.models.answers import Answer
from app.schemas.answers import SaveAnswerPayload
from app.models.answers import Answer


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


@pytest.mark.asyncio
async def test_save_answers_success(session_cleanup: AsyncSession) -> None:
    """
    /answers/save_answers
    ユーザーの回答を正常に保存できるケースのテスト
    """
    transport = ASGITransport(app=app)  # type: ignore
    headers = {"Authorization": "Bearer fake_token"}

    # リクエストボディの準備
    data = {
        "title": "Test Title",
        "relatedFiles": ["file1.pdf", "file2.pdf"],
        "responses": [
            {
                "question_id": "Q1",
                "question_text": "What is Python?",
                "choices": {
                    "choice_a": "A programming language",
                    "choice_b": "A snake",
                    "choice_c": "A fruit",
                    "choice_d": "A car brand",
                },
                "user_selected_choice": "choice_a",
                "correct_choice": "choice_a",
                "is_correct": True,
                "explanation": "Python is a programming language.",
            },
            {
                "question_id": "Q2",
                "question_text": "What is 2 + 2?",
                "choices": {"choice_a": "3", "choice_b": "4", "choice_c": "5", "choice_d": "6"},
                "user_selected_choice": "choice_b",
                "correct_choice": "choice_b",
                "is_correct": True,
                "explanation": "2 + 2 equals 4.",
            },
        ],
    }

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/answers/save_answers", json=data, headers=headers)

    # レスポンスのアサーション
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "回答が正常に保存されました。"

    # DBに保存されているか確認 (成功パスのみ簡易確認)
    # 本来はAnswerレコードの内容を検証する等、もう少し踏み込んだテストが可能です
    stmt = select(Answer).where(Answer.user_id == "test_user")  # テスト用モックユーザー
    results = await session_cleanup.execute(stmt)
    answers = results.scalars().all()
    # 2つの回答（responses）が保存されていることを期待
    assert len(answers) == 2


@pytest.mark.asyncio
async def test_get_my_answers_success(session_cleanup: AsyncSession) -> None:
    """
    /answers/list
    ユーザーが自分の回答データ一覧を正常に取得できるケースのテスト
    """
    # 事前にAnswerを作成してDBに登録
    now_jst = datetime.now(timezone(timedelta(hours=9)))
    answer1 = Answer(
        title="Title1",
        related_files=["file1.pdf"],
        question_id="Q1",  # 個別フィールドとして保存
        question_text="What is Python?",
        choice_a="A programming language",
        choice_b="A snake",
        choice_c="A fruit",
        choice_d="A car brand",
        user_selected_choice="choice_a",
        correct_choice="choice_a",
        is_correct=True,
        explanation="Python is a programming language.",
        user_id="test_user",
        created_at=now_jst,
        updated_at=now_jst,
    )
    answer2 = Answer(
        title="Title2",
        related_files=["file2.pdf"],
        question_id="Q2",  # 個別フィールドとして保存
        question_text="What is 2 + 2?",
        choice_a="3",
        choice_b="4",
        choice_c="5",
        choice_d="6",
        user_selected_choice="choice_b",
        correct_choice="choice_b",
        is_correct=True,
        explanation="2 + 2 equals 4.",
        user_id="test_user",
        created_at=now_jst,
        updated_at=now_jst,
    )
    session_cleanup.add_all([answer1, answer2])
    await session_cleanup.commit()
    await session_cleanup.refresh(answer1)
    await session_cleanup.refresh(answer2)

    transport = ASGITransport(app=app)  # type: ignore
    headers = {"Authorization": "Bearer fake_token"}

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/answers/list", headers=headers)

    # レスポンスのアサーション
    assert response.status_code == 200
    json_data = response.json()

    assert len(json_data) == 2
    # それぞれのフィールドが返ってきているかを確認
    titles = [item["title"] for item in json_data]
    assert "Title1" in titles
    assert "Title2" in titles


@pytest.mark.asyncio
async def test_delete_answer_success(session_cleanup: AsyncSession) -> None:
    """
    /answers/delete/{answer_id}
    ユーザーが自分の特定の回答を正常に削除できるケースのテスト
    """
    # 事前にAnswerを作成してDBに登録
    now_jst = datetime.now(timezone(timedelta(hours=9)))
    answer = Answer(
        title="Delete Target",
        related_files=["file1.pdf"],
        question_id="Q1",
        question_text="Test Question",
        choice_a="A",
        choice_b="B",
        choice_c="C",
        choice_d="D",
        user_selected_choice="choice_a",
        correct_choice="choice_a",
        is_correct=True,
        explanation="Test explanation",
        user_id="test_user",
        created_at=now_jst,
        updated_at=now_jst,
    )
    session_cleanup.add(answer)
    await session_cleanup.commit()
    await session_cleanup.refresh(answer)

    answer_id = answer.id

    transport = ASGITransport(app=app)  # type: ignore
    headers = {"Authorization": "Bearer fake_token"}

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete(f"/answers/delete/{answer_id}", headers=headers)

    # コミット処理を追加
    await session_cleanup.commit()

    # レスポンスのアサーション
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "回答が正常に削除されました。"

    # DBから本当に削除されたか確認
    stmt = select(Answer).where(Answer.id == answer_id)
    result = await session_cleanup.execute(stmt)
    deleted_answer = result.scalar_one_or_none()
    assert deleted_answer is None


@pytest.mark.asyncio
async def test_bulk_delete_answers_success(session_cleanup: AsyncSession) -> None:
    """
    /answers/bulk_delete
    ユーザーが自分の複数の回答を正常に一括削除できるケースのテスト
    """
    now_jst = datetime.now(timezone(timedelta(hours=9)))

    # テストデータ作成
    answers_to_delete = []
    for i in range(3):
        ans = Answer(
            title=f"Bulk Title {i}",
            related_files=["file1.pdf"],
            question_id=f"Q{i}",
            question_text=f"Question {i}",
            choice_a="A",
            choice_b="B",
            choice_c="C",
            choice_d="D",
            user_selected_choice="choice_a",
            correct_choice="choice_a",
            is_correct=True,
            explanation=f"Explanation {i}",
            user_id="test_user",
            created_at=now_jst,
            updated_at=now_jst,
        )
        answers_to_delete.append(ans)

    # DBにデータを追加
    session_cleanup.add_all(answers_to_delete)
    await session_cleanup.commit()
    for ans in answers_to_delete:
        await session_cleanup.refresh(ans)

    # 削除対象のID
    answer_ids_to_delete = [ans.id for ans in answers_to_delete]
    print(f"Test IDs to delete: {answer_ids_to_delete}")

    # 削除API呼び出し
    transport = ASGITransport(app=app)  # type: ignore
    headers = {"Authorization": "Bearer fake_token"}

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.request(
            "DELETE",
            "/answers/bulk_delete",
            headers=headers,
            json={"answer_ids": answer_ids_to_delete},
        )

    # APIレスポンスの確認
    assert response.status_code == 200
    resp_data = response.json()
    assert "deleted_ids" in resp_data
    assert len(resp_data["deleted_ids"]) == len(answer_ids_to_delete)
    assert set(resp_data["deleted_ids"]) == set(answer_ids_to_delete)

    # 新しいセッションでDB状態を確認
    async with AsyncSession(session_cleanup.bind) as new_session:
        stmt = select(Answer).where(Answer.id.in_(answer_ids_to_delete))
        result = await new_session.execute(stmt)
        remaining_answers = result.scalars().all()
        print(f"Remaining answers in DB: {remaining_answers}")  # デバッグ用
        assert len(remaining_answers) == 0  # 全て削除されていることを確認


@pytest.mark.asyncio
async def test_save_answers_invalid_payload(session_cleanup: AsyncSession) -> None:
    """
    /answers/save_answers
    不正なリクエストデータでエラーが返されることを確認するテスト
    """
    transport = ASGITransport(app=app)  # type: ignore
    headers = {"Authorization": "Bearer fake_token"}

    # リクエストボディが不完全
    invalid_data = {
        "title": "Test Title",
        # "responses" フィールドが欠落
    }

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/answers/save_answers", json=invalid_data, headers=headers)

    # エラーのアサーション
    assert response.status_code == 422
    error_data = response.json()
    assert "detail" in error_data


@pytest.mark.asyncio
async def test_get_my_answers_no_data(session_cleanup: AsyncSession) -> None:
    """
    /answers/list
    回答データが存在しない場合のテスト
    """
    transport = ASGITransport(app=app)  # type: ignore
    headers = {"Authorization": "Bearer fake_token"}

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/answers/list", headers=headers)

    # レスポンスのアサーション
    assert response.status_code == 200
    json_data = response.json()
    assert json_data == []  # 空リストが返されることを確認


@pytest.mark.asyncio
async def test_delete_answer_not_found(session_cleanup: AsyncSession) -> None:
    """
    /answers/delete/{answer_id}
    存在しない回答IDを削除しようとした場合のテスト
    """
    transport = ASGITransport(app=app)  # type: ignore
    headers = {"Authorization": "Bearer fake_token"}

    non_existent_answer_id = 9999  # 存在しないID

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete(f"/answers/delete/{non_existent_answer_id}", headers=headers)

    # レスポンスのアサーション
    assert response.status_code == 404
    error_data = response.json()
    assert error_data["detail"] == "回答が見つかりません。"


@pytest.mark.asyncio
async def test_bulk_delete_answers_partial_failure(session_cleanup: AsyncSession) -> None:
    """
    /answers/bulk_delete
    一部の回答IDが見つからない場合のテスト
    """
    now_jst = datetime.now(timezone(timedelta(hours=9)))

    # 正常なデータ1つだけをDBに追加
    answer = Answer(
        title="Valid Answer",
        related_files=["file1.pdf"],
        question_id="Q1",
        question_text="Test Question",
        choice_a="A",
        choice_b="B",
        choice_c="C",
        choice_d="D",
        user_selected_choice="choice_a",
        correct_choice="choice_a",
        is_correct=True,
        explanation="Test explanation",
        user_id="test_user",
        created_at=now_jst,
        updated_at=now_jst,
    )
    session_cleanup.add(answer)
    await session_cleanup.commit()
    await session_cleanup.refresh(answer)

    # 存在しないIDを含むリクエスト
    request_data = {"answer_ids": [answer.id, 9999]}  # 存在しないIDを含む

    transport = ASGITransport(app=app)  # type: ignore
    headers = {"Authorization": "Bearer fake_token"}

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.request(
            "DELETE",
            "/answers/bulk_delete",
            headers=headers,
            json=request_data,
        )

    # レスポンスのアサーション
    assert response.status_code == 200
    resp_data = response.json()

    # 削除成功と失敗の両方を確認
    assert answer.id in resp_data["deleted_ids"]
    assert 9999 in resp_data["not_found_ids"]
    assert len(resp_data["unauthorized_ids"]) == 0


@pytest.mark.asyncio
async def test_bulk_delete_answers_no_ids(session_cleanup: AsyncSession) -> None:
    """
    /answers/bulk_delete
    空のIDリストを渡した場合のテスト
    """
    transport = ASGITransport(app=app)  # type: ignore
    headers = {"Authorization": "Bearer fake_token"}

    # 空のリクエストデータ
    empty_request: dict[str, list[int]] = {"answer_ids": []}

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.request(
            "DELETE",
            "/answers/bulk_delete",
            headers=headers,
            json=empty_request,
        )

    # レスポンスのアサーション
    assert response.status_code == 400
    error_data = response.json()
    assert error_data["detail"] == "削除する回答IDのリストが空です。"