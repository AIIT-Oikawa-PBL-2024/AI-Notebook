import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

# .envファイルから環境変数を読み込む
load_dotenv()


# 環境変数からデータベースのユーザー名、パスワード、ホスト、ポートを取得する
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "dev-db")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME=os.getenv("DB_NAME", "dev-db")

# データベースURLを作成
ASYNC_DB_URL = (
    f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8"
)

# データベースエンジンを作成
async_engine = create_async_engine(ASYNC_DB_URL, echo=True)

# セッションを作成
async_session = async_sessionmaker(
    autoflush=False, bind=async_engine, class_=AsyncSession
)


# ベースモデルを作成
Base = declarative_base()


# データベースのセッションを取得
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
