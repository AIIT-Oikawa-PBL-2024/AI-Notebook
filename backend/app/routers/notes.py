from typing import Sequence, Union

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import app.cruds.notes as notes_cruds
import app.schemas.notes as notes_schemas
from app.database import get_db

router = APIRouter()

db_dependency = Depends(get_db)


router = APIRouter(
    prefix="/notes",
    tags=["notes"],
)


@router.get("/")
async def get_notes(
    db: AsyncSession = db_dependency, offset: int = 0, limit: int = 100
) -> Sequence[notes_schemas.NoteResponse]:
    """
    ノートのリストを取得するエンドポイント

    :param db: データベースセッション
    :type db: AsyncSession
    :param offset: オフセット
    :type offset: int
    :param limit: 取得するノートの最大数
    :type limit: int
    :return: ノートのリスト
    :rtype: Sequence[notes_schemas.NoteResponse]
    """

    return await notes_cruds.get_notes(db, offset=offset, limit=limit)


@router.get("/{user_id}/notes")
async def get_notes_by_user(
    user_id: str, db: AsyncSession = db_dependency, offset: int = 0, limit: int = 100
) -> Sequence[notes_schemas.NoteByCurrentUserResponse]:
    """
    指定されたユーザーのノートのリストを取得するエンドポイント

    :param user_id: ユーザーID
    :type user_id: str
    :param db: データベースセッション
    :type db: AsyncSession
    :param offset: オフセット
    :type offset: int
    :param limit: 取得するノートの数
    :type limit: int
    :return: ノートのリスト
    :rtype: Sequence[notes_schemas.NoteByCurrentUserResponse]
    """

    return await notes_cruds.get_notes_by_user_id(
        db, user_id=user_id, offset=offset, limit=limit
    )


@router.post("/")
async def create_note(
    note: notes_schemas.NoteCreate,
    db: AsyncSession = db_dependency,
) -> notes_schemas.NoteCreateResponse:
    """
    ノートを作成するエンドポイント

    :param note: ノートの作成情報
    :type note: notes_schemas.NoteCreate
    :param db: データベースセッション
    :type db: AsyncSession
    :return: 作成されたノート
    :rtype: notes_schemas.NoteCreateResponse
    """

    return await notes_cruds.create_note(db, note)


@router.put("/{note_id}")
async def update_note(
    note_id: int, note: notes_schemas.NoteUpdate, db: AsyncSession = db_dependency
) -> Union[dict[str, str], notes_schemas.NoteUpdateResponse]:
    """
    ノートを更新するエンドポイント

    :param note_id: ノートのID
    :type note_id: int
    :param note: ノートの更新情報
    :type note: notes_schemas.NoteUpdate
    :param db: データベースセッション
    :type db: AsyncSession
    :return: 更新されたノート
    :rtype: Union[dict[str, str], notes_schemas.NoteUpdateResponse]
    """

    existing_note = await notes_cruds.get_note_by_id(db, note_id)
    if existing_note is None:
        raise HTTPException(status_code=404, detail="ノートが見つかりません。")
    response = await notes_cruds.update_note(db, note_id, note)
    return response


@router.delete("/{note_id}")
async def delete_note(note_id: int, db: AsyncSession = db_dependency) -> bool:
    """
    ノートを削除するエンドポイント

    :param note_id: ノートのID
    :type note_id: int
    :param db: データベースセッション
    :type db: AsyncSession
    :return: 削除の成否
    :rtype: bool
    """

    existing_note = await notes_cruds.get_note_by_id(db, note_id)
    if existing_note is None:
        raise HTTPException(status_code=404, detail="ノートが見つかりません。")
    return await notes_cruds.delete_note(db, note_id)
