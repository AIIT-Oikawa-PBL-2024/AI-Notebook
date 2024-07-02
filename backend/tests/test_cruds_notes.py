from typing import AsyncGenerator
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

import app.cruds.notes as notes_cruds
import app.schemas.notes as notes_shemas
import app.models.notes as notes_models


@pytest.fixture
async def session(
    setup_and_teardown_database: AsyncGenerator[AsyncSession, None],
) -> AsyncGenerator[AsyncSession, None]:
    async with setup_and_teardown_database as session:  # type: ignore
        yield session


@pytest.fixture
async def create_test_note(
    session: AsyncSession, test_user_id: int
) -> notes_models.Note:
    note_create = notes_shemas.NoteCreate(
        title="test_title",
        content="test_content",
        user_id=test_user_id,
    )
    note = await notes_cruds.create_note(session, note_create)
    return note


@pytest.mark.asyncio
async def test_create_note(session: AsyncSession, test_user_id: int) -> None:
    note_create = notes_shemas.NoteCreate(
        title="test_title",
        content="test_content",
        user_id=test_user_id,
    )
    note = await notes_cruds.create_note(session, note_create)

    assert note.id is not None
    assert note.title == "test_title"
    assert note.content == "test_content"


@pytest.mark.asyncio
async def test_get_note_by_id(
    session: AsyncSession, create_test_note: notes_models.Note
) -> None:
    note_id = int(create_test_note.id)
    note = await notes_cruds.get_note_by_id(session, note_id)

    assert note is not None
    assert note.title == "test_title"
    assert note.content == "test_content"
    assert note.user_id == create_test_note.user_id


@pytest.mark.asyncio
async def test_get_notes(
    session: AsyncSession, create_test_note: notes_models.Note
) -> None:
    notes = await notes_cruds.get_notes(session, offset=0, limit=10)

    assert len(notes) > 0
    assert notes[0].title == "test_title"
    assert notes[0].content == "test_content"


@pytest.mark.asyncio
async def test_get_notes_by_user_id(
    session: AsyncSession, create_test_note: notes_models.Note
) -> None:
    notes = await notes_cruds.get_notes_by_user_id(
        session, user_id=int(create_test_note.user_id), offset=0, limit=10
    )

    assert len(notes) > 0
    assert notes[0].title == "test_title"
    assert notes[0].content == "test_content"
    assert notes[0].user_id == create_test_note.user_id


@pytest.mark.asyncio
async def test_update_note(
    session: AsyncSession, create_test_note: notes_models.Note
) -> None:
    note_id = int(create_test_note.id)
    note_update = notes_shemas.NoteUpdate(
        title="updated_title", content="updated_content"
    )
    updated_note = await notes_cruds.update_note(session, note_id, note_update)
    assert updated_note is not None
    assert updated_note.title == "updated_title"
    assert updated_note.content == "updated_content"
    assert updated_note.user_id == create_test_note.user_id


@pytest.mark.asyncio
async def test_delete_note(
    session: AsyncSession, create_test_note: notes_models.Note
) -> None:
    note_id = int(create_test_note.id)
    response = await notes_cruds.delete_note(session, note_id)
    assert response == True
