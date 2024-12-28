import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import app.cruds.answers as answers_cruds
import app.models.answers as answers_models
import app.schemas.answers as answers_schemas
from app.database import get_db
from app.utils.user_auth import get_uid

# ロギング設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

router = APIRouter(
    prefix="/answers",
    tags=["answers"],
)

# 日本時間のタイムゾーン
JST = timezone(timedelta(hours=9))

# 依存関係
db_dependency = Depends(get_db)


@router.post(
    "/save_answers",
    summary="ユーザーの回答を保存するエンドポイント",
    response_model=Dict[str, str],
)
async def save_answers(
    payload: answers_schemas.SaveAnswerPayload,
    db: AsyncSession = db_dependency,
    uid: str = Depends(get_uid),  # ユーザーIDを取得
) -> Dict[str, str]:
    """
    ユーザーの回答データを受け取り、データベースに保存します。

    - **title**: 問題集のタイトル
    - **relatedFiles**: 関連ファイルのリスト
    - **responses**: ユーザーの回答データリスト
    """
    try:
        # 現在の日本時間を取得
        current_time = datetime.now(JST)

        # CRUD操作を実行し、データベースに保存
        await answers_cruds.save_answers_to_db(db, payload, uid, current_time)
        logger.info(f"User {uid} の回答が正常に保存されました。件数: {len(payload.responses)}")
        return {"message": "回答が正常に保存されました。"}
    except Exception as e:
        # エラーログを出力
        logger.error(f"回答の保存中にエラーが発生しました: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="内部サーバーエラーが発生しました。") from e


@router.get(
    "/list",
    summary="ユーザーの回答データを取得するエンドポイント",
    response_model=List[answers_schemas.AnswerResponse],
)
async def get_my_answers(
    db: AsyncSession = db_dependency,
    uid: str = Depends(get_uid),  # ユーザーIDを取得
) -> List[answers_schemas.AnswerResponse]:
    """
    現在のユーザーの回答データを取得します。
    """
    try:
        answers = await answers_cruds.get_answers_by_user(db, uid)
        logger.info(f"User {uid} の回答データを取得しました。件数: {len(answers)}")
        return answers
    except Exception as e:
        logger.error(f"回答の取得中にエラーが発生しました: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="内部サーバーエラーが発生しました。") from e


@router.delete(
    "/delete/{answer_id}",
    summary="ユーザーの特定の回答を削除するエンドポイント",
    response_model=answers_schemas.DeleteResponse,
)
async def delete_answer(
    answer_id: int,
    db: AsyncSession = db_dependency,
    uid: str = Depends(get_uid),  # ユーザーIDを取得
) -> answers_schemas.DeleteResponse:
    """
    指定された回答IDを持つユーザーの回答を削除します。

    - **answer_id**: 削除対象の回答ID
    """
    try:
        # 回答を取得
        stmt = select(answers_models.Answer).where(answers_models.Answer.id == answer_id)
        result = await db.execute(stmt)
        original_answer: Optional[answers_models.Answer] = result.scalars().first()

        if not original_answer:
            logger.warning(
                f"User {uid} が回答ID {answer_id} を削除しようとしましたが、見つかりませんでした。"
            )
            raise HTTPException(status_code=404, detail="回答が見つかりません。")

        # CRUD関数を呼び出して削除
        await answers_cruds.delete_answer_by_user(db, original_answer, uid)

        return answers_schemas.DeleteResponse(message="回答が正常に削除されました。")

    except HTTPException as he:
        raise he
    except ValueError as ve:
        logger.warning(f"User {uid} の削除試行が不正です: {ve}")
        raise HTTPException(status_code=403, detail=str(ve)) from ve
    except Exception as e:
        logger.error(f"回答の削除中にエラーが発生しました: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="内部サーバーエラーが発生しました。") from e


@router.delete(
    "/bulk_delete",
    summary="ユーザーの複数の回答を一括で削除するエンドポイント",
    response_model=answers_schemas.DeleteAnswersResult,
)
async def bulk_delete_answers(
    request: answers_schemas.BulkDeleteRequest,
    db: AsyncSession = db_dependency,
    uid: str = Depends(get_uid),
) -> answers_schemas.DeleteAnswersResult:
    """
    指定された回答IDリストを持つユーザーの回答を一括で削除します。

    - **answer_ids**: 削除対象の回答IDのリスト
    """
    try:
        if not request.answer_ids:
            raise HTTPException(status_code=400, detail="削除する回答IDのリストが空です。")

        result = await answers_cruds.delete_answers_by_user(db, request.answer_ids, uid)

        if result.deleted_ids:
            logger.info(f"User {uid} の回答ID {result.deleted_ids} が正常に削除されました。")
        if result.not_found_ids:
            logger.warning(f"回答ID {result.not_found_ids} が見つかりませんでした。")
        if result.unauthorized_ids:
            logger.warning(
                f"User {uid} が所有していない回答ID {result.unauthorized_ids} の削除を試みました。"
            )

        return result

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"回答の一括削除中にエラーが発生しました: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="内部サーバーエラーが発生しました。") from e
