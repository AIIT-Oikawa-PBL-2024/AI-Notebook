import os
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Connection

from app.database import Base
from app.models.answers import Answer  # noqa: F401
from app.models.exercises import Exercise  # noqa: F401
from app.models.exercises_files import exercise_file  # noqa: F401
from app.models.exercises_user_answer import ExerciseUserAnswer  # noqa: F401
from app.models.files import File  # noqa: F401
from app.models.notes import Note  # noqa: F401
from app.models.outputs import Output  # noqa: F401
from app.models.outputs_files import output_file  # noqa: F401

# .envファイルを読み込む
load_dotenv()

# Alembic Config objectを取得し、.iniファイルの値にアクセスする
config = context.config

# ロギングの設定
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# モデルのメタデータを追加（自動生成のサポートのため）
target_metadata = Base.metadata

# 環境変数からDATABASE_URLを構築
db_user = os.getenv("DB_USER", "root")
db_password = os.getenv("DB_PASSWORD", "")
db_host = os.getenv("DB_HOST", "dev-db")
db_port = os.getenv("DB_PORT", "3306")
db_name = os.getenv("DB_NAME", "dev-db")
database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

if not database_url:
    raise ValueError("The sqlalchemy.url configuration option must be a string.")

config.set_main_option("sqlalchemy.url", database_url)


# オフラインモードのマイグレーション関数
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        raise ValueError("The sqlalchemy.url configuration option must be a string.")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# オンラインモードのマイグレーション関数
def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        raise ValueError("The sqlalchemy.url configuration option must be a string.")

    connectable = create_engine(
        url,
        future=True,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
