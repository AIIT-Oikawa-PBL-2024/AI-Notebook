import os
from typing import AsyncGenerator, Generator
import pytest
from dotenv import load_dotenv
from sqlalchemy import delete, select
from sqlalchemy.sql import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from httpx import ASGITransport, AsyncClient
from app.database import Base, get_db
from app.main import app
from app.models.files import File
from app.models.outputs import Output
from app.models.exercises import Exercise
from unittest.mock import Mock, patch
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials
import jwt
import time

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

# テスト環境であることを示す環境変数を設定
os.environ["TESTING"] = "True"


# データベースセッションの依存関係をオーバーライド
async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


# FastAPIアプリのget_db依存関係をオーバーライド
app.dependency_overrides[get_db] = override_get_db


# データベースのセットアップとクリーンアップを行うフィクスチャ
@pytest.fixture(scope="function", autouse=True)
async def setup_and_teardown_database() -> AsyncGenerator[AsyncSession, None]:
    print("\n=== Starting Database Setup ===")  # デバッグ用

    try:
        # まず既存のテーブルを削除
        async with engine.begin() as conn:
            print("Dropping existing tables...")  # デバッグ用
            await conn.run_sync(Base.metadata.drop_all)
            print("Existing tables dropped successfully")  # デバッグ用
    except Exception as e:
        print(f"Error dropping tables: {e}")  # デバッグ用
        pass

    try:
        # テーブルを作成
        async with engine.begin() as conn:
            print("Creating database tables...")  # デバッグ用
            await conn.run_sync(Base.metadata.create_all)
            print("Database tables created successfully")  # デバッグ用

            # テーブル一覧を確認
            result = await conn.execute(text("SHOW TABLES"))
            tables = result.fetchall()
            print("Created tables:", tables)  # デバッグ用

            # exercisesテーブルの構造を確認
            result = await conn.execute(text("DESCRIBE exercises"))
            structure = result.fetchall()
            print("Exercises table structure:", structure)  # デバッグ用
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise

    print("Creating test session...")  # デバッグ用
    async with TestingSessionLocal() as session:
        # 全てのクリーンアップを1つのトランザクションで実行
        try:
            print("Cleaning up existing data...")  # デバッグ用
            await session.execute(delete(Exercise))
            await session.execute(delete(Output))
            await session.execute(delete(File))
            await session.commit()
            print("Data cleanup successful")  # デバッグ用
        except Exception as e:
            await session.rollback()
            print(f"Error during cleanup: {e}")
            raise

        print("Setup complete - yielding session")  # デバッグ用
        yield session

    print("Test finished - starting cleanup")  # デバッグ用
    try:
        async with engine.begin() as conn:
            print("Dropping tables in cleanup...")  # デバッグ用
            await conn.run_sync(Base.metadata.drop_all)
            print("Cleanup complete")  # デバッグ用
    except Exception as e:
        print(f"Error during final cleanup: {e}")  # デバッグ用
        pass

    await engine.dispose()
    print("=== Database Setup and Cleanup Finished ===")  # デバッグ用


# テスト用ユーザーIDを提供するフィクスチャ
@pytest.fixture
def test_user_id() -> str:
    return "firebase_test_user_123456"


# sessionフィクスチャを提供するフィクスチャを定義
@pytest.fixture
async def session(
    setup_and_teardown_database: AsyncGenerator[AsyncSession, None],
) -> AsyncGenerator[AsyncSession, None]:
    async with setup_and_teardown_database as session:  # type: ignore
        yield session
    await session.close()


# テスト用のJWTトークンを生成する関数
def generate_test_token(uid: str = "test_user") -> str:
    payload = {
        "uid": uid,
        "exp": int(time.time()) + 3600,  # 1時間有効
        "iat": int(time.time()),
    }
    secret = "test_secret"  # テスト用の秘密鍵
    return jwt.encode(payload, secret, algorithm="HS256")


# 認証をモックする関数
def mock_authenticate_request(request: Request, credentials: HTTPAuthorizationCredentials) -> None:
    request.state.uid = "test_user"
    return None


# テスト用のダミーFirebase認証情報
dummy_firebase_credentials = {
    "type": "service_account",
    "project_id": "dummy-project",
    "private_key_id": "dummy-key-id",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC9hxWe/UJH1QAF\n-----END PRIVATE KEY-----\n",
    "client_email": "dummy@dummy-project.iam.gserviceaccount.com",
    "client_id": "123456789",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/dummy%40dummy-project.iam.gserviceaccount.com",
}


# 環境変数をモック
@pytest.fixture(autouse=True)
def mock_env_vars() -> Generator:
    with patch.dict(os.environ, {"FIREBASE_CREDENTIALS": str(dummy_firebase_credentials)}):
        yield


# 認証をモックするフィクスチャ
@pytest.fixture(autouse=True)
def mock_auth() -> Generator:
    with patch("app.utils.user_auth.authenticate_request", mock_authenticate_request):
        yield


# AsyncClientを提供するフィクスチャ
@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        yield client
