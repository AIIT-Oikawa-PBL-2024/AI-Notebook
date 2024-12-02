import logging
import os

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from app.database import Base
from app.models.exercises import Exercise  # noqa: F401
from app.models.exercises_files import exercise_file  # noqa: F401
from app.models.files import File  # noqa: F401
from app.models.notes import Note  # noqa: F401
from app.models.outputs import Output  # noqa: F401
from app.models.outputs_files import output_file  # noqa: F401

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 環境変数から設定を読み込む
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "dev-db")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "dev-db")


def get_database_url(include_db_name: bool = False) -> str:
    """データベースURLを生成する"""
    base_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"
    return (
        f"{base_url}/{DB_NAME}?charset=utf8mb4"
        if include_db_name
        else f"{base_url}/?charset=utf8mb4"
    )


def get_engine(include_db_name: bool = False) -> Engine:
    """SQLAlchemy エンジンを取得する"""
    return create_engine(get_database_url(include_db_name))


def database_exists() -> bool:
    """データベースが存在するか確認する"""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SHOW DATABASES LIKE '{DB_NAME}'"))
            return result.fetchone() is not None
    except SQLAlchemyError as e:
        logger.error(f"データベースの確認中にエラーが発生しました: {e}")
        return False


def create_database() -> None:
    """データベースを作成する"""
    if not database_exists():
        engine = get_engine()
        try:
            with engine.connect() as conn:
                conn.execute(text(f"CREATE DATABASE `{DB_NAME}`"))
            logger.info(f"データベース '{DB_NAME}' を作成しました")
        except SQLAlchemyError as e:
            logger.error(f"データベースの作成に失敗しました: {e}")
            raise


def create_tables() -> None:
    """テーブルを作成する"""
    engine = get_engine(include_db_name=True)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("テーブルを作成しました")
    except SQLAlchemyError as e:
        logger.error(f"テーブルの作成に失敗しました: {e}")
        raise


def get_new_tables(engine: Engine) -> set:
    """新しく作成されたテーブルを取得する"""
    inspector = inspect(engine)
    before = set(inspector.get_table_names())
    Base.metadata.create_all(bind=engine)
    after = set(inspector.get_table_names())
    return after - before


def update_and_create_tables() -> None:
    """データベースをアップデートし、必要に応じて新しいテーブルを作成する"""
    engine = get_engine(include_db_name=True)
    try:
        new_tables = get_new_tables(engine)
        if new_tables:
            logger.info(f"新しいテーブルが作成されました: {', '.join(new_tables)}")
        else:
            logger.info("新しいテーブルは作成されませんでした")
        logger.info("データベースを正常にアップデートしました")
    except SQLAlchemyError as e:
        logger.error(f"データベースのアップデートに失敗しました: {e}")
        raise


def initialize_database() -> None:
    """データベースの初期化プロセスを実行する"""
    try:
        create_database()
        create_tables()
        update_and_create_tables()
        logger.info("データベースの初期化が完了しました")
    except SQLAlchemyError as e:
        logger.error(f"データベースの初期化中にエラーが発生しました: {e}")
        raise


if __name__ == "__main__":
    initialize_database()
