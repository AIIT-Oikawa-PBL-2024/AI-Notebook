from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

import app.models.files as files_models
import app.schemas.files as files_schemas


# 新しいファイルを作成する関数
async def create_file(
    db: AsyncSession, file_create: files_schemas.FileCreate
) -> files_models.File:
    """
    新しいファイルを作成する関数

    :param db: データベースセッション
    :type db: AsyncSession
    :param file_create: 作成するファイルの情報
    :type file_create: files_schemas.FileCreate
    :return: 作成されたファイルのインスタンス
    :rtype: files_models.File
    """
    file = files_models.File(**file_create.model_dump())
    db.add(file)  # ファイルをデータベースに追加
    await db.commit()  # 変更をコミット
    await db.refresh(file)  # ファイルの情報をリフレッシュ
    return file


# 全ファイルを取得する関数
async def get_files(db: AsyncSession) -> list[files_schemas.File]:
    """
    全ファイルを取得する関数

    :param db: データベースセッション
    :type db: AsyncSession
    :return: ファイルのリスト
    :rtype: list[files_schemas.File]
    """
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
    """
    ファイルIDから特定のファイルを取得する関数

    :param db: データベースセッション
    :type db: AsyncSession
    :param file_id: 取得するファイルのID
    :type file_id: int
    :return: 取得されたファイルのインスタンス、存在しない場合はNone
    :rtype: files_models.File | None
    """
    result: Result = await db.execute(
        select(files_models.File).filter(files_models.File.id == file_id)
    )
    return result.scalars().first()  # 結果の最初のファイルを返す



# ファイル名とユーザーIDから特定のファイルを削除する関数
async def delete_file_by_name_and_userid(
    db: AsyncSession, file_name: str, user_id: int
) -> None:
    """
    指定されたファイル名とユーザーIDに基づいてファイルを削除します。

    :param db: データベースセッション
    :type db: AsyncSession
    :param file_name: 削除するファイルの名前
    :type file_name: str
    :param user_id: ファイルを所有するユーザーのID
    :type user_id: int
    :return: None
    :rtype: None
    """
    try:
        result: Result = await db.execute(
            select(files_models.File)
            .filter(files_models.File.file_name == file_name)
            .filter(files_models.File.user_id == user_id)
        )
        for file in result.scalars():
            await db.delete(file)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise e
        
