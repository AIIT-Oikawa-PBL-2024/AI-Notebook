import pytest
from sqlalchemy.exc import OperationalError

from app.database import async_engine, get_db


# DB接続のテスト
@pytest.mark.asyncio
async def test_db_connection() -> None:
    try:
        # 接続を試みる
        async with async_engine.connect() as conn:
            assert conn is not None
    except OperationalError:
        pytest.fail("Database connection failed.")


# get_db関数のテスト
@pytest.mark.asyncio
async def test_get_db() -> None:
    async for db in get_db():
        assert db is not None
