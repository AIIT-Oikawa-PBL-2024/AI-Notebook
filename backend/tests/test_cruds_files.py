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
    """
    データベースのセットアップとテアダウンを行う非同期セッションフィクスチャ。

    :param setup_and_teardown_database: データベースのセットアップとテアダウンを行う非同期ジェネレータ
    :type setup_and_teardown_database: AsyncGenerator[AsyncSession, None]
    :yield: 非同期セッション
    :rtype: AsyncGenerator[AsyncSession, None]
    """
    async with setup_and_teardown_database as session:  # type: ignore
        yield session


# ファイル作成のテスト
@pytest.mark.asyncio
async def test_create_file(session: AsyncSession, test_user_id: str) -> None:
    """
    ファイル作成のテスト。

    :param session: 非同期セッション
    :type session: AsyncSession
    :param test_user_id: テストユーザーのID
    :type test_user_id: str
    :return: None
    """
    file_create = files_schemas.FileCreate(
        file_name="test_file.pdf",
        file_size=12345,
        user_id=test_user_id,
        created_at=datetime.now(JST),
    )
    file = await files_cruds.create_file(session, file_create, test_user_id)

    assert file.id is not None
    assert file.file_name == "test_file.pdf"
    assert file.file_size == 12345
    assert file.user_id == test_user_id


# ファイル取得のテスト
@pytest.mark.asyncio
async def test_get_files(session: AsyncSession, test_user_id: str) -> None:
    """
    ファイル取得のテスト。

    :param session: 非同期セッション
    :type session: AsyncSession
    :param test_user_id: テストユーザーのID
    :type test_user_id: str
    :return: None
    """
    file_create = files_schemas.FileCreate(
        file_name="test_file.pdf",
        file_size=12345,
        user_id=test_user_id,
        created_at=datetime.now(JST),
    )
    await files_cruds.create_file(session, file_create, test_user_id)

    files = await files_cruds.get_files_by_user_id(session, test_user_id)
    assert len(files) > 0
    assert files[0].file_name == "test_file.pdf"
    assert files[0].file_size == 12345
    assert files[0].user_id == test_user_id


# ファイルIDによるファイル取得のテスト
@pytest.mark.asyncio
async def test_get_file_by_id(session: AsyncSession, test_user_id: str) -> None:
    """
    ファイルIDによるファイル取得のテスト。

    :param session: 非同期セッション
    :type session: AsyncSession
    :param test_user_id: テストユーザーのID
    :type test_user_id: str
    :return: None
    """
    file_create = files_schemas.FileCreate(
        file_name="test_file.pdf",
        file_size=12345,
        user_id=test_user_id,
        created_at=datetime.now(JST),
    )
    file = await files_cruds.create_file(session, file_create, test_user_id)
    file_id = int(file.id)

    retrieved_file = await files_cruds.get_file_by_id_and_user_id(
        session, file_id, test_user_id
    )
    assert retrieved_file is not None
    assert retrieved_file.id == file.id
    assert retrieved_file.file_name == file.file_name
    assert retrieved_file.file_size == file.file_size
    assert retrieved_file.user_id == file.user_id


# 存在しないファイルIDによるファイル取得のテスト
@pytest.mark.asyncio
async def test_get_file_by_id_not_found(session: AsyncSession) -> None:
    """
    存在しないファイルIDによるファイル取得のテスト。

    :param session: 非同期セッション
    :type session: AsyncSession
    :return: None
    """
    retrieved_file = await files_cruds.get_file_by_id_and_user_id(
        session, 9999, "test_user_id"
    )
    assert retrieved_file is None


# ファイル名のリストとユーザーIDによるファイル削除のテスト
@pytest.mark.asyncio
async def test_delete_file_by_name(session: AsyncSession, test_user_id: str) -> None:
    """
    ファイル削除のテスト。

    :param session: 非同期セッション
    :type session: AsyncSession
    :param test_user_id: テストユーザーのID
    :type test_user_id: str
    :return: None
    """
    file_create = files_schemas.FileCreate(
        file_name="test_file.pdf",
        file_size=12345,
        user_id=test_user_id,
        created_at=datetime.now(JST),
    )
    file = await files_cruds.create_file(session, file_create, test_user_id)

    await files_cruds.delete_file_by_name_and_userid(
        session, "test_file.pdf", test_user_id
    )
    file_id = int(file.id)

    retrieved_file = await files_cruds.get_file_by_id_and_user_id(
        session, file_id, test_user_id
    )
    assert retrieved_file is None
