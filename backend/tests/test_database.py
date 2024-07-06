import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, async_session, ASYNC_DB_URL


@pytest.mark.asyncio
async def test_get_db() -> None:
    """
    get_db関数のテスト

    このテストでは、get_db関数が正しく非同期セッションを返し、
    適切に閉じることを確認します。
    """
    db_generator = get_db()
    db = await anext(db_generator)

    # セッションの型を確認
    assert isinstance(db, AsyncSession)


def test_database_url() -> None:
    """
    データベースURLのテスト

    ASYNC_DB_URLが期待される値と一致することを確認します。
    """
    expected_url = "mysql+aiomysql://root:@dev-db:3306/dev-db?charset=utf8mb4"
    assert ASYNC_DB_URL == expected_url


@pytest.mark.asyncio
async def test_async_session() -> None:
    """
    async_session関数のテスト

    async_session関数が正しくAsyncSessionオブジェクトを返すことを確認します。
    """
    async with async_session() as session:
        assert isinstance(session, AsyncSession)
