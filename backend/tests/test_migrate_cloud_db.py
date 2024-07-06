import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from app.migrate_cloud_db import (
    database_exists,
    create_database,
    create_tables,
    update_and_create_tables,
    initialize_database,
)


@pytest.mark.asyncio
async def test_database_exists() -> None:
    """
    database_exists関数のテスト。

    以下のケースをテストします：
    1. データベースが存在する場合
    2. データベースが存在しない場合
    3. エラーが発生した場合
    """
    with patch("app.migrate_cloud_db.get_engine") as mock_get_engine:
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_get_engine.return_value = mock_engine

        # データベースが存在する場合
        mock_connection.execute.return_value.fetchone.return_value = True
        assert database_exists() == True

        # データベースが存在しない場合
        mock_connection.execute.return_value.fetchone.return_value = None
        assert database_exists() == False

        # エラーが発生した場合
        mock_connection.execute.side_effect = SQLAlchemyError("テストエラー")
        assert database_exists() == False


@pytest.mark.asyncio
async def test_create_database() -> None:
    """
    create_database関数のテスト。

    以下のケースをテストします：
    1. データベースが存在しない場合、新しく作成されることを確認
    2. データベースが既に存在する場合、作成が行われないことを確認
    """
    with (
        patch("app.migrate_cloud_db.get_engine") as mock_get_engine,
        patch("app.migrate_cloud_db.database_exists") as mock_database_exists,
    ):
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_get_engine.return_value = mock_engine

        # データベースが存在しない場合
        mock_database_exists.return_value = False
        create_database()
        mock_connection.execute.assert_called_once()

        # データベースが既に存在する場合
        mock_database_exists.return_value = True
        create_database()
        assert mock_connection.execute.call_count == 1  # 追加の呼び出しがないことを確認


@pytest.mark.asyncio
async def test_create_tables() -> None:
    """
    create_tables関数のテスト。

    Base.metadata.create_allが正しく呼び出されることを確認します。
    """
    with (
        patch("app.migrate_cloud_db.get_engine") as mock_get_engine,
        patch("app.migrate_cloud_db.Base") as mock_base,
    ):
        mock_engine = MagicMock()
        mock_get_engine.return_value = mock_engine

        create_tables()
        mock_base.metadata.create_all.assert_called_once_with(bind=mock_engine)


@pytest.mark.asyncio
async def test_update_and_create_tables() -> None:
    """
    update_and_create_tables関数のテスト。

    以下のケースをテストします：
    1. 新しいテーブルがある場合の動作
    2. 新しいテーブルがない場合の動作
    """
    with (
        patch("app.migrate_cloud_db.get_engine") as mock_get_engine,
        patch("app.migrate_cloud_db.get_new_tables") as mock_get_new_tables,
    ):
        mock_engine = MagicMock()
        mock_get_engine.return_value = mock_engine

        # 新しいテーブルがある場合
        mock_get_new_tables.return_value = {"new_table1", "new_table2"}
        update_and_create_tables()
        mock_get_new_tables.assert_called_once_with(mock_engine)

        # 新しいテーブルがない場合
        mock_get_new_tables.return_value = set()
        update_and_create_tables()


@pytest.mark.asyncio
async def test_initialize_database() -> None:
    """
    initialize_database関数のテスト。

    以下のケースをテストします：
    1. 正常に実行された場合、各関数が順に呼び出されることを確認
    2. エラーが発生した場合、例外が発生することを確認
    """
    with (
        patch("app.migrate_cloud_db.create_database") as mock_create_database,
        patch("app.migrate_cloud_db.create_tables") as mock_create_tables,
        patch(
            "app.migrate_cloud_db.update_and_create_tables"
        ) as mock_update_and_create_tables,
    ):
        initialize_database()

        mock_create_database.assert_called_once()
        mock_create_tables.assert_called_once()
        mock_update_and_create_tables.assert_called_once()

        # エラーが発生した場合
        mock_create_database.side_effect = SQLAlchemyError("テストエラー")
        with pytest.raises(SQLAlchemyError):
            initialize_database()
