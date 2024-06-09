from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

import app.models.files as files_models
import app.schemas.files as files_schemas


# 新しいファイルを作成する関数
async def create_file(
    db: AsyncSession, file_create: files_schemas.FileCreate
) -> files_models.File:
    # ファイルのインスタンスを作成
    file = files_models.File(**file_create.model_dump())
    db.add(file)  # ファイルをデータベースに追加
    await db.commit()  # 変更をコミット
    await db.refresh(file)  # ファイルの情報をリフレッシュ
    return file


# 全ファイルを取得する関数
async def get_files(db: AsyncSession) -> list[files_schemas.File]:
    # ファイル情報を選択
    result: Result = await db.execute(
        select(
            files_models.File.id,
            files_models.File.file_name,
            files_models.File.file_size,
            files_models.File.user_id,
            files_models.File.created_at,
        )
    )
    files = result.all()  # 結果を取得
    # ファイル情報をスキーマに変換して返す
    return [
        files_schemas.File(
            id=file.id,
            file_name=file.file_name,
            file_size=file.file_size,
            user_id=file.user_id,
            created_at=file.created_at,
        )
        for file in files
    ]


# ファイルIDから特定のファイルを取得する関数
async def get_file_by_id(db: AsyncSession, file_id: int) -> files_models.File | None:
    # 指定されたファイルIDのファイル情報を選択
    result: Result = await db.execute(
        select(files_models.File).filter(files_models.File.id == file_id)
    )
    return result.scalars().first()  # 結果の最初のファイルを返す


# ファイルIDから特定のファイルを削除する関数
async def delete_file(db: AsyncSession, original_file: files_models.File) -> None:
    await db.delete(original_file)  # ファイルを削除
    await db.commit()  # 変更をコミット
    return
