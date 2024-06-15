# GitHub Actions用のconftest.py　テスト用データベースのホストのみ変更
import os
from typing import AsyncGenerator

import pytest
from dotenv import load_dotenv
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app
from app.models.files import File
from app.models.outputs import Output
from app.models.users import User

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数からデータベースのユーザー名、パスワード、ホスト、ポートを取得する
TEST_DB_USER = os.getenv("TEST_DB_USER", "root")
TEST_DB_PASSWORD = os.getenv("TEST_DB_PASSWORD", "")
# TEST_DB_HOST = os.getenv("TEST_DB_HOST", "test-db")
TEST_DB_PORT = os.getenv("TEST_DB_PORT", "3306")
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "test-db")

# テスト用データベースのURL
TEST_DB_URL = f"mysql+aiomysql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@127.0.0.1:{TEST_DB_PORT}/{TEST_DB_NAME}?charset=utf8mb4"

# エンジンとセッションを作成
engine = create_async_engine(TEST_DB_URL, echo=True)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


# データベースセッションの依存関係をオーバーライド
async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


# FastAPIアプリのget_db依存関係をオーバーライド
app.dependency_overrides[get_db] = override_get_db


# データベースのセットアップとクリーンアップを行うフィクスチャ
@pytest.fixture(scope="function")
async def setup_and_teardown_database() -> AsyncGenerator[AsyncSession, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        await session.execute(delete(File))
        await session.commit()

        await session.execute(delete(Output))
        await session.commit()

        await session.execute(delete(User).where(User.email == "test@example.com"))
        await session.commit()

        new_user = User(
            username="testuser", email="test@example.com", password="password"
        )
        session.add(new_user)
        await session.commit()

        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


# テスト用ユーザーIDを提供するフィクスチャ
@pytest.fixture
async def test_user_id(
    setup_and_teardown_database: AsyncGenerator[AsyncSession, None],
) -> int:
    async with setup_and_teardown_database as session:  # type: ignore
        result = await session.execute(
            select(User).where(User.email == "test@example.com")
        )
        user = result.scalar()
        return user.id
