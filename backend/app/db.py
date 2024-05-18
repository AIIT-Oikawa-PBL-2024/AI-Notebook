import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数からデータベースのユーザー名、パスワード、ホスト、ポートを取得する
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "3306")

# 非同期データベースURLを作成
ASYNC_DB_URL = (
    f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/dev-db?charset=utf8"
)

# 非同期エンジンを作成
async_engine = create_async_engine(ASYNC_DB_URL, echo=True)
async_session = sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
)

# ベースクラスを作成
Base = declarative_base()


# データベースセッションを取得する非同期ジェネレータ関数
async def get_db():
    async with async_session() as session:
        yield session
