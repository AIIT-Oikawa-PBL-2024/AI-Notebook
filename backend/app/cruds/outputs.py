from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

import app.models.outputs as outputs_models
import app.schemas.outputs as outputs_schemas


# 新しい学習帳を作成する関数
async def create_output(
    db: AsyncSession, output_create: outputs_schemas.OutputCreate
) -> outputs_models.Output:
    # 学習帳のインスタンスを作成
    output = outputs_models.Output(**output_create.model_dump())
    db.add(output)  # 学習帳をデータベースに追加
    await db.commit()  # 変更をコミット
    await db.refresh(output)  # 学習帳の情報をリフレッシュ
    return output


# 全学習帳を取得する関数
async def get_outputs(db: AsyncSession) -> list[outputs_schemas.Output]:
    # 学習帳情報を選択
    result: Result = await db.execute(
        select(
            outputs_models.Output.id,
            outputs_models.Output.output,
            outputs_models.Output.user_id,
            outputs_models.Output.created_at,
        )
    )
    outputs = result.all()  # 結果を取得
    # 学習帳情報をスキーマに変換して返す
    return [
        outputs_schemas.Output(
            id=output.id,
            output=output.output,
            user_id=output.user_id,
            created_at=output.created_at,
        )
        for output in outputs
    ]


# 学習帳IDから特定の学習帳を取得する関数
async def get_output_by_id(
    db: AsyncSession, output_id: int
) -> outputs_models.Output | None:
    # 指定された学習帳IDの学習帳情報を選択
    result: Result = await db.execute(
        select(outputs_models.Output).filter(outputs_models.Output.id == output_id)
    )
    return result.scalars().first()  # 結果の最初の学習帳を返す


# 学習帳IDから特定の学習帳を削除する関数
async def delete_output(
    db: AsyncSession, original_output: outputs_models.Output
) -> None:
    await db.delete(original_output)  # 学習帳を削除
    await db.commit()  # 変更をコミット
    return
