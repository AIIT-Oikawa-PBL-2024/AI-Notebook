import logging

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import app.models.files as files_models
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
    # OutputCreateからファイル名を取り出し、残りのデータでOutputを作成
    output_data = output_create.model_dump(exclude={"file_names"})
    output = outputs_models.Output(**output_data)

    # 先にoutputを保存してIDを取得
    db.add(output)
    await db.flush()

    # ファイル名からファイルを取得して関連付け
    if output_create.file_names:
        files_result: Result = await db.execute(
            select(files_models.File).filter(
                files_models.File.file_name.in_(output_create.file_names)
            )
        )
        files = files_result.scalars().all()
        output.files.extend(files)

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
            outputs_models.Output.title,
            outputs_models.Output.id,
            outputs_models.Output.style,
            outputs_models.Output.output,
            outputs_models.Output.user_id,
            outputs_models.Output.created_at,
        )
    )
    outputs = result.all()
    return [
        outputs_schemas.Output(
            title=output.title,
            id=output.id,
            output=output.output,
            style=output.style,
            user_id=output.user_id,
            created_at=output.created_at,
        )
        for output in outputs
    ]


async def get_output_by_id_and_user(
    db: AsyncSession, output_id: int, user_id: str
) -> outputs_models.Output | None:
    """
    学習帳IDから特定の学習帳を取得する関数

    :param db: データベースセッション
    :type db: AsyncSession
    :param output_id: 取得する学習帳のID
    :type output_id: int
    :param user_id: ユーザーID（Firebase UID）
    :type user_id: str
    :return: 学習帳の情報またはNone
    :rtype: outputs_models.Output | None
    """
    result: Result = await db.execute(
        select(outputs_models.Output)
        .options(selectinload(outputs_models.Output.files))
        .filter(outputs_models.Output.id == output_id)
        .filter(outputs_models.Output.user_id == user_id)
    )

    return result.scalars().first()


async def delete_output(db: AsyncSession, original_output: outputs_models.Output) -> None:
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


async def get_outputs_by_user(db: AsyncSession, user_id: str) -> list[outputs_schemas.OutputRead]:
    """
    ユーザーIDに基づいてAI出力を取得する関数。
    関連するファイル情報も含めて取得し、作成日時の降順でソートします。

    :param db: データベースセッション
    :type db: AsyncSession
    :param user_id: ユーザーID（Firebase UID）
    :type user_id: str
    :return: ユーザーに関連付けられたAI出力のリスト
    :rtype: list[outputs_schemas.OutputRead]
    :raises SQLAlchemyError: データベース操作中にエラーが発生した場合
    """
    try:
        result: Result = await db.execute(
            select(outputs_models.Output)
            .options(selectinload(outputs_models.Output.files))
            .filter(outputs_models.Output.user_id == user_id)
            .order_by(outputs_models.Output.created_at.desc())
        )
        outputs = result.scalars().all()
        return [outputs_schemas.OutputRead.model_validate(output) for output in outputs]

    except SQLAlchemyError as e:
        logging.error(f"Error retrieving outputs for user {user_id}: {e}")
        raise


async def get_output_files_by_user(
    db: AsyncSession, output_id: int, user_id: str
) -> list[files_models.File]:
    """
    ユーザーIDとAI出力IDから関連付けられたファイルを取得する関数

    :param db: データベースセッション
    :type db: AsyncSession
    :param output_id: AIID
    :type output_id: int
    :param user_id: ユーザーID（Firebase UID）
    :type user_id: str
    :return: 関連付けられたファイルのリスト
    :rtype: list[files_models.File]
    :raises ValueError: AI出力が見つからない場合、またはユーザーが権限を持っていない場合
    :raises SQLAlchemyError: データベース操作中にエラーが発生した場合
    """
    try:
        result: Result = await db.execute(
            select(outputs_models.Output)
            .options(selectinload(outputs_models.Output.files))
            .filter(outputs_models.Output.id == output_id)
            .filter(outputs_models.Output.user_id == user_id)
        )
        output = result.scalar_one_or_none()

        if output is None:
            raise ValueError(f"Output with ID {output_id} not found for user {user_id}")

        return output.files

    except SQLAlchemyError as e:
        logging.error(f"Error retrieving files for output {output_id} and user {user_id}: {e}")
        raise
