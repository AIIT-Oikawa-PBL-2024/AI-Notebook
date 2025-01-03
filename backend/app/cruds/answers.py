import logging
from datetime import datetime
from typing import List

from sqlalchemy import desc, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import app.models.answers as answers_models
import app.schemas.answers as answers_schemas

# ロギング設定
logger = logging.getLogger(__name__)


async def save_answers_to_db(
    db: AsyncSession,
    payload: answers_schemas.SaveAnswerPayload,
    user_id: str,
    current_time: datetime,
) -> None:
    """
    ユーザーの回答データをデータベースに保存します。

    :param db: SQLAlchemyの非同期セッション
    :param payload: SaveAnswerPayloadオブジェクト
    :param user_id: ユーザーID
    :param current_time: 現在の日本時間
    """
    try:
        answers = [
            answers_models.Answer(
                title=payload.title,
                related_files=payload.relatedFiles,
                question_id=response.question_id,
                question_text=response.question_text,
                choice_a=response.choices.choice_a,
                choice_b=response.choices.choice_b,
                choice_c=response.choices.choice_c,
                choice_d=response.choices.choice_d,
                user_selected_choice=response.user_selected_choice,
                correct_choice=response.correct_choice,
                is_correct=response.is_correct,
                explanation=response.explanation,
                user_id=user_id,
                created_at=current_time,
                updated_at=current_time,
            )
            for response in payload.responses
        ]
        db.add_all(answers)  # 複数の回答を一度に追加
        await db.commit()
        logger.info(f"User {user_id} の回答が正常に保存されました。件数: {len(answers)}")
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"データベース操作中にエラーが発生しました: {e}", exc_info=True)
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"予期しないエラーが発生しました: {e}", exc_info=True)
        raise


async def get_answers_by_user(
    db: AsyncSession, user_id: str, skip: int = 0, limit: int = 100
) -> List[answers_schemas.AnswerResponse]:
    """
    指定されたユーザーIDに紐づく回答データを取得します（ページネーション対応）。

    :param db: SQLAlchemyの非同期セッション
    :param user_id: ユーザーID
    :param skip: 取得をスキップする件数
    :param limit: 取得する最大件数
    :return: 回答データのリスト
    """
    try:
        result = await db.execute(
            select(answers_models.Answer)
            .where(answers_models.Answer.user_id == user_id)
            .order_by(desc(answers_models.Answer.created_at))
            .offset(skip)
            .limit(limit)
        )
        db_answers = result.scalars().all()
        answers = [answers_schemas.AnswerResponse.model_validate(answer) for answer in db_answers]
        logger.info(f"User {user_id} の回答データを取得しました。件数: {len(answers)}")
        return answers
    except SQLAlchemyError as e:
        logger.error(f"データベース操作中にエラーが発生しました: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"予期しないエラーが発生しました: {e}", exc_info=True)
        raise


async def count_user_answers(db: AsyncSession, user_id: str) -> int:
    """
    指定されたユーザーIDに紐づく回答データの総件数を取得します。

    :param db: SQLAlchemyの非同期セッション
    :param user_id: ユーザーID
    :return: 回答データの総件数
    """
    try:
        result = await db.execute(
            select(func.count(answers_models.Answer.id)).where(
                answers_models.Answer.user_id == user_id
            )
        )
        total_count = result.scalar_one()
        logger.info(f"User {user_id} の回答データ総件数: {total_count}")
        return total_count
    except SQLAlchemyError as e:
        logger.error(f"データベース操作中にエラーが発生しました: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"予期しないエラーが発生しました: {e}", exc_info=True)
        raise


async def delete_answer_by_user(
    db: AsyncSession, original_answer: answers_models.Answer, user_id: str
) -> None:
    """
    ユーザーIDと回答の情報から特定の回答を削除する関数

    :param db: データベースセッション
    :type db: AsyncSession
    :param original_answer: 削除する回答の情報
    :type original_answer: answers_models.Answer
    :param user_id: ユーザーID（Firebase UID）
    :type user_id: str
    :return: None
    :rtype: None
    :raises ValueError: 指定されたユーザーが回答の所有者でない場合
    :raises SQLAlchemyError: データベース操作中にエラーが発生した場合
    """
    try:
        # ユーザーIDの確認
        if original_answer.user_id != user_id:
            raise ValueError("User is not authorized to delete this answer")

        # 回答の削除（cascade=True の設定により関連レコードも削除される場合があります）
        await db.delete(original_answer)
        await db.commit()
        logger.info(f"User {user_id} の回答ID {original_answer.id} を削除しました。")

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"データベース操作中にエラーが発生しました: {e}", exc_info=True)
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"予期しないエラーが発生しました: {e}", exc_info=True)
        raise


async def delete_answers_by_user(
    db: AsyncSession, answer_ids: List[int], user_id: str
) -> answers_schemas.DeleteAnswersResult:
    """
    一括でユーザーの回答を削除します。

    :param db: データベースセッション
    :type db: AsyncSession
    :param answer_ids: 削除対象の回答IDのリスト
    :type answer_ids: List[int]
    :param user_id: ユーザーID（Firebase UID）
    :type user_id: str
    :return: 削除結果
    :rtype: DeleteAnswersResult
    :raises SQLAlchemyError: データベース操作中にエラーが発生した場合
    """
    try:
        # 回答を一括取得
        stmt = select(answers_models.Answer).where(answers_models.Answer.id.in_(answer_ids))
        result = await db.execute(stmt)
        answers = result.scalars().all()

        # 所有権の確認
        owned_answers = [answer for answer in answers if answer.user_id == user_id]
        unauthorized_answers = [int(answer.id) for answer in answers if answer.user_id != user_id]
        found_ids = [answer.id for answer in answers]

        # 存在しないIDの確認
        not_found_ids = [aid for aid in answer_ids if aid not in found_ids]

        # 削除対象
        to_delete = owned_answers

        # 削除処理
        if to_delete:
            for answer in to_delete:
                await db.delete(answer)
            await db.commit()
            deleted_ids = [int(answer.id) for answer in to_delete]
            logger.info(f"User {user_id} の回答ID {deleted_ids} を削除しました。")
        else:
            deleted_ids = []

        return answers_schemas.DeleteAnswersResult(
            deleted_ids=deleted_ids,
            not_found_ids=not_found_ids,
            unauthorized_ids=unauthorized_answers,
        )

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"データベース操作中にエラーが発生しました: {e}", exc_info=True)
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"予期しないエラーが発生しました: {e}", exc_info=True)
        raise
