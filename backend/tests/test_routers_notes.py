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
        transport=ASGITransport(app),  # type: ignore
        base_url="http://testserver",
    ) as ac:
        yield ac


@pytest.fixture
async def create_test_note(
    session: AsyncSession, test_user_id: str
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
    headers = {"Authorization": "Bearer fake_token"}
    response = await client.get("/notes/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == "test_title"
    assert data[0]["content"] == "test_content"


@pytest.mark.asyncio
async def test_get_notes_by_user_id(
    client: AsyncClient, create_test_note: notes_models.Note
) -> None:
    headers = {"Authorization": "Bearer fake_token"}
    user_id = "firebase_test_user_123456"
    response = await client.get(f"/notes/{user_id}/notes", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == "test_title"
    assert data[0]["content"] == "test_content"
    assert data[0]["user_id"] == user_id


@pytest.mark.asyncio
async def test_create_note(client: AsyncClient, test_user_id: str) -> None:
    headers = {"Authorization": "Bearer fake_token"}
    user_id = "firebase_test_user_123456"
    note_create = notes_schemas.NoteCreate(
        title="test_title",
        content="test_content",
        user_id=user_id,
    )
    response = await client.post("/notes/", json=note_create.model_dump(), headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "test_title"
    assert data["content"] == "test_content"


@pytest.mark.asyncio
async def test_update_note(
    client: AsyncClient, create_test_note: notes_models.Note
) -> None:
    headers = {"Authorization": "Bearer fake_token"}
    user_id = "firebase_test_user_123456"
    note_id = create_test_note.id
    note_update = notes_schemas.NoteUpdate(
        title="updated_title", content="updated_content"
    )
    response = await client.put(f"/notes/{note_id}", json=note_update.model_dump(), headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "updated_title"
    assert data["content"] == "updated_content"
    assert data["user_id"] == user_id


@pytest.mark.asyncio
async def test_delete_note(
    client: AsyncClient, create_test_note: notes_models.Note
) -> None:
    headers = {"Authorization": "Bearer fake_token"}
    note_id = create_test_note.id
    response = await client.delete(f"/notes/{note_id}", headers=headers)
    assert response.status_code == 200
    assert response.json() == True
    deleted_response = await client.delete(f"/notes/{note_id}", headers=headers)
    assert deleted_response.status_code == 404
