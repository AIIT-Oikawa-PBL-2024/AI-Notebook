from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

import app.cruds.files as files_cruds
import app.schemas.files as files_schemas

# 日本時間のタイムゾーン
JST = timezone(timedelta(hours=9))


# sessionフィクスチャを提供するフィクスチャを定義
@pytest.fixture
async def session(
    setup_and_teardown_database: AsyncGenerator[AsyncSession, None],
) -> AsyncGenerator[AsyncSession, None]:
    async with setup_and_teardown_database as session:  # type: ignore
        yield session


# ファイル作成のテスト
@pytest.mark.asyncio
async def test_create_file(session: AsyncSession, test_user_id: int) -> None:
    file_create = files_schemas.FileCreate(
        file_name="test_file.pdf",
        file_size=12345,
        user_id=test_user_id,
        created_at=datetime.now(JST),
    )
    file = await files_cruds.create_file(session, file_create)

    assert file.id is not None
    assert file.file_name == "test_file.pdf"
    assert file.file_size == 12345
    assert file.user_id == test_user_id


# ファイル取得のテスト
@pytest.mark.asyncio
async def test_get_files(session: AsyncSession, test_user_id: int) -> None:
    file_create = files_schemas.FileCreate(
        file_name="test_file.pdf",
        file_size=12345,
        user_id=test_user_id,
        created_at=datetime.now(JST),
    )
    await files_cruds.create_file(session, file_create)

    files = await files_cruds.get_files(session)
    assert len(files) > 0
    assert files[0].file_name == "test_file.pdf"
    assert files[0].file_size == 12345
    assert files[0].user_id == test_user_id


# ファイルIDによるファイル取得のテスト
@pytest.mark.asyncio
async def test_get_file_by_id(session: AsyncSession, test_user_id: int) -> None:
    file_create = files_schemas.FileCreate(
        file_name="test_file.pdf",
        file_size=12345,
        user_id=test_user_id,
        created_at=datetime.now(JST),
    )
    file = await files_cruds.create_file(session, file_create)
    file_id = int(file.id)

    retrieved_file = await files_cruds.get_file_by_id(session, file_id)
    assert retrieved_file is not None
    assert retrieved_file.id == file.id
    assert retrieved_file.file_name == file.file_name
    assert retrieved_file.file_size == file.file_size
    assert retrieved_file.user_id == file.user_id


# 存在しないファイルIDによるファイル取得のテスト
@pytest.mark.asyncio
async def test_get_file_by_id_not_found(session: AsyncSession) -> None:
    retrieved_file = await files_cruds.get_file_by_id(session, 9999)
    assert retrieved_file is None


# ファイル削除のテスト
@pytest.mark.asyncio
async def test_delete_file(session: AsyncSession, test_user_id: int) -> None:
    file_create = files_schemas.FileCreate(
        file_name="test_file.pdf",
        file_size=12345,
        user_id=test_user_id,
        created_at=datetime.now(JST),
    )
    file = await files_cruds.create_file(session, file_create)

    await files_cruds.delete_file(session, file)
    file_id = int(file.id)

    retrieved_file = await files_cruds.get_file_by_id(session, file_id)
    assert retrieved_file is None


# ファイル名のリストによるファイル削除のテスト
@pytest.mark.asyncio
async def test_delete_file_by_name(session: AsyncSession, test_user_id: int) -> None:
    file_create = files_schemas.FileCreate(
        file_name="test_file.pdf",
        file_size=12345,
        user_id=test_user_id,
        created_at=datetime.now(JST),
    )
    file = await files_cruds.create_file(session, file_create)

    await files_cruds.delete_file_by_name(session, "test_file.pdf")
    file_id = int(file.id)

    retrieved_file = await files_cruds.get_file_by_id(session, file_id)
    assert retrieved_file is None
