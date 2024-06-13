from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

import app.cruds.outputs as outputs_cruds
import app.schemas.outputs as outputs_schemas

# 日本時間のタイムゾーン
JST = timezone(timedelta(hours=9))


# sessionフィクスチャを提供するフィクスチャを定義
@pytest.fixture
async def session(
    setup_and_teardown_database: AsyncGenerator[AsyncSession, None],
) -> AsyncGenerator[AsyncSession, None]:
    async with setup_and_teardown_database as session:  # type: ignore
        yield session


# 学習帳作成のテスト
@pytest.mark.asyncio
async def test_create_output(session: AsyncSession, test_user_id: int) -> None:
    output_create = outputs_schemas.OutputCreate(
        output="テストマークダウン🚀",
        user_id=test_user_id,
        created_at=datetime.now(JST),
    )
    output = await outputs_cruds.create_output(session, output_create)
    assert output.id is not None
    assert output.output == "テストマークダウン🚀"
    assert output.user_id == test_user_id


# 学習帳取得のテスト
@pytest.mark.asyncio
async def test_get_outputs(session: AsyncSession, test_user_id: int) -> None:
    output_create = outputs_schemas.OutputCreate(
        output="テストマークダウン🚀",
        user_id=test_user_id,
        created_at=datetime.now(JST),
    )
    await outputs_cruds.create_output(session, output_create)

    outputs = await outputs_cruds.get_outputs(session)
    assert len(outputs) > 0
    assert outputs[0].output == "テストマークダウン🚀"
    assert outputs[0].user_id == test_user_id


# 学習帳IDによる学習帳取得のテスト
@pytest.mark.asyncio
async def test_get_output_by_id(session: AsyncSession, test_user_id: int) -> None:
    output_create = outputs_schemas.OutputCreate(
        output="テストマークダウン🚀",
        user_id=test_user_id,
        created_at=datetime.now(JST),
    )
    output = await outputs_cruds.create_output(session, output_create)
    output_id = int(output.id)

    retrieved_output = await outputs_cruds.get_output_by_id(session, output_id)
    assert retrieved_output is not None
    assert retrieved_output.id == output.id
    assert retrieved_output.output == output.output
    assert retrieved_output.user_id == output.user_id


# 存在しない学習帳IDによる学習帳取得のテスト
@pytest.mark.asyncio
async def test_get_output_by_id_not_found(session: AsyncSession) -> None:
    retrieved_output = await outputs_cruds.get_output_by_id(session, 9999)
    assert retrieved_output is None


# 学習帳削除のテスト
@pytest.mark.asyncio
async def test_delete_output(session: AsyncSession, test_user_id: int) -> None:
    output_create = outputs_schemas.OutputCreate(
        output="テストマークダウン🚀",
        user_id=test_user_id,
        created_at=datetime.now(JST),
    )
    output = await outputs_cruds.create_output(session, output_create)

    await outputs_cruds.delete_output(session, output)
    output_id = int(output.id)

    retrieved_output = await outputs_cruds.get_output_by_id(session, output_id)
    assert retrieved_output is None
