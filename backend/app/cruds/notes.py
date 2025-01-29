from datetime import datetime, timedelta, timezone
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

import app.models.notes as notes_models
import app.schemas.notes as notes_schemas

# 日本時間のタイムゾーン
JST = timezone(timedelta(hours=9))


async def create_note(db: AsyncSession, note_create: notes_schemas.NoteCreate) -> notes_models.Note:
    note_dict = note_create.model_dump()
    now_japan = datetime.now(JST)
    note_dict.update({"created_at": now_japan, "updated_at": now_japan})
    note = notes_models.Note(**note_dict)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


async def get_note_by_id(db: AsyncSession, note_id: int) -> Optional[notes_models.Note]:
    result: Result = await db.execute(
        select(notes_models.Note).where(notes_models.Note.id == note_id)
    )
    note = result.scalar()
    return note


async def get_notes(db: AsyncSession, offset: int, limit: int) -> Sequence[notes_models.Note]:
    result: Result = await db.execute(select(notes_models.Note).offset(offset).limit(limit))
    notes = result.scalars().all()
    return notes


async def get_notes_by_user_id(
    db: AsyncSession, user_id: str, offset: int, limit: int
) -> Sequence[notes_models.Note]:
    result: Result = await db.execute(
        select(notes_models.Note)
        .where(notes_models.Note.user_id == user_id)
        .offset(offset)
        .limit(limit)
    )
    notes = result.scalars().all()
    return notes


async def update_note(
    db: AsyncSession, note_id: int, note_update: notes_schemas.NoteUpdate
) -> notes_models.Note:
    result: Result = await db.execute(
        select(notes_models.Note).where(notes_models.Note.id == note_id)
    )
    note = result.scalar()
    assert note is not None  # MypyはNoneが返らないことを認識できないためassertする

    for key, value in note_update.model_dump().items():
        setattr(note, key, value)

    # 日本時間の現在日時を取得
    now_japan = datetime.now(JST)
    note.updated_at = now_japan

    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


async def delete_note(db: AsyncSession, note_id: int) -> bool:
    note = await get_note_by_id(db, note_id)
    await db.delete(note)
    await db.commit()
    return True
