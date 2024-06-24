from typing import Union

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import app.cruds.notes as notes_cruds
import app.cruds.users as users_cruds
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
) -> list[notes_schemas.NoteResponse]:
    return await notes_cruds.get_notes(db, offset=offset, limit=limit)


@router.get("/{user_id}/notes")
async def get_notes_by_user(
    user_id: int, db: AsyncSession = db_dependency, offset: int = 0, limit: int = 100
) -> list[notes_schemas.NoteByCurrentUserResponse]:
    user = await users_cruds.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません。")
    return await notes_cruds.get_notes_by_user_id(
        db, user_id=user_id, offset=offset, limit=limit
    )


@router.post("/")
async def create_note(
    note: notes_schemas.NoteCreate,
    db: AsyncSession = db_dependency,
) -> notes_schemas.NoteCreateResponse:
    return await notes_cruds.create_note(db, note)


@router.put("/{note_id}")
async def update_note(
    note_id: int, note: notes_schemas.NoteUpdate, db: AsyncSession = db_dependency
) -> Union[dict[str, str], notes_schemas.NoteUpdateResponse]:
    existing_note = await notes_cruds.get_note_by_id(db, note_id)
    if existing_note is None:
        raise HTTPException(status_code=404, detail="ノートが見つかりません。")
    response = await notes_cruds.update_note(db, note_id, note)
    return response


@router.delete("/{note_id}")
async def delete_note(note_id: int, db: AsyncSession = db_dependency) -> bool:
    existing_note = await notes_cruds.get_note_by_id(db, note_id)
    if existing_note is None:
        raise HTTPException(status_code=404, detail="ノートが見つかりません。")
    return await notes_cruds.delete_note(db, note_id)
