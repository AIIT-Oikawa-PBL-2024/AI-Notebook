import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.main import app
import app.schemas.notes as notes_schemas
import app.models.notes as notes_models
import app.cruds.notes as notes_cruds


@pytest.fixture
async def session(
    setup_and_teardown_database: AsyncGenerator[AsyncSession, None],
) -> AsyncGenerator[AsyncSession, None]:
    async with setup_and_teardown_database as session:  # type: ignore
        yield session


@pytest.fixture
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_db] = lambda: session
    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://testserver"
    ) as ac:
        yield ac


@pytest.fixture
async def create_test_note(
    session: AsyncSession, test_user_id: int
) -> notes_models.Note:
    note_create = notes_schemas.NoteCreate(
        title="test_title",
        content="test_content",
        user_id=test_user_id,
    )
    note = await notes_cruds.create_note(session, note_create)
    return note


@pytest.mark.asyncio
async def test_get_notes(
    client: AsyncClient, create_test_note: notes_models.Note
) -> None:
    response = await client.get("/notes/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == "test_title"
    assert data[0]["content"] == "test_content"


@pytest.mark.asyncio
async def test_get_notes_by_user_id(
    client: AsyncClient, create_test_note: notes_models.Note
) -> None:
    user_id = create_test_note.user_id
    response = await client.get(f"/notes/{user_id}/notes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == "test_title"
    assert data[0]["content"] == "test_content"
    assert data[0]["user_id"] == user_id


@pytest.mark.asyncio
async def test_create_note(client: AsyncClient, test_user_id: int) -> None:
    note_create = notes_schemas.NoteCreate(
        title="test_title",
        content="test_content",
        user_id=test_user_id,
    )
    response = await client.post("/notes/", json=note_create.model_dump())
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "test_title"
    assert data["content"] == "test_content"


@pytest.mark.asyncio
async def test_update_note(
    client: AsyncClient, create_test_note: notes_models.Note
) -> None:
    note_id = create_test_note.id
    note_update = notes_schemas.NoteUpdate(
        title="updated_title", content="updated_content"
    )
    response = await client.put(f"/notes/{note_id}", json=note_update.model_dump())
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "updated_title"
    assert data["content"] == "updated_content"
    assert data["user_id"] == create_test_note.user_id


@pytest.mark.asyncio
async def test_delete_note(
    client: AsyncClient, create_test_note: notes_models.Note
) -> None:
    note_id = create_test_note.id
    response = await client.delete(f"/notes/{note_id}")
    assert response.status_code == 200
    assert response.json() == True
    deleted_response = await client.delete(f"/notes/{note_id}")
    assert deleted_response.status_code == 404
