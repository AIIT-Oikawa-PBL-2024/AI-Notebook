from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

import app.models.outputs as outputs_models
import app.schemas.outputs as outputs_schemas


async def create_output(
    db: AsyncSession, output_create: outputs_schemas.OutputCreate
) -> outputs_models.Output:
    """
    新しい学習帳を作成する関数

    :param db: データベースセッション
    :type db: AsyncSession
    :param output_create: 作成する学習帳の情報
    :type output_create: outputs_schemas.OutputCreate
    :return: 作成された学習帳の情報
    :rtype: outputs_models.Output
    """
    output = outputs_models.Output(**output_create.model_dump())
    db.add(output)
    await db.commit()
    await db.refresh(output)
    return output


async def get_outputs(db: AsyncSession) -> list[outputs_schemas.Output]:
    """
    全学習帳を取得する関数

    :param db: データベースセッション
    :type db: AsyncSession
    :return: 学習帳のリスト
    :rtype: list[outputs_schemas.Output]
    """
    result: Result = await db.execute(
        select(
            outputs_models.Output.id,
            outputs_models.Output.output,
            outputs_models.Output.user_id,
            outputs_models.Output.created_at,
        )
    )
    outputs = result.all()
    return [
        outputs_schemas.Output(
            id=output.id,
            output=output.output,
            user_id=output.user_id,
            created_at=output.created_at,
        )
        for output in outputs
    ]


async def get_output_by_id(
    db: AsyncSession, output_id: int
) -> outputs_models.Output | None:
    """
    学習帳IDから特定の学習帳を取得する関数

    :param db: データベースセッション
    :type db: AsyncSession
    :param output_id: 取得する学習帳のID
    :type output_id: int
    :return: 学習帳の情報またはNone
    :rtype: outputs_models.Output | None
    """
    result: Result = await db.execute(
        select(outputs_models.Output).filter(outputs_models.Output.id == output_id)
    )
    return result.scalars().first()


async def delete_output(
    db: AsyncSession, original_output: outputs_models.Output
) -> None:
    """
    学習帳IDから特定の学習帳を削除する関数

    :param db: データベースセッション
    :type db: AsyncSession
    :param original_output: 削除する学習帳の情報
    :type original_output: outputs_models.Output
    :return: None
    :rtype: None
    """
    await db.delete(original_output)
    await db.commit()
    return
