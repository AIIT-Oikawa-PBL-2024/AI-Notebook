from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

import app.models.files as files_models
import app.schemas.files as files_schemas


async def create_file(
    db: AsyncSession, file_create: files_schemas.FileCreate, uid: str
) -> files_models.File:
    """
    新しいファイルを作成する関数

    :param db: データベースセッション
    :type db: AsyncSession
    :param file_create: 作成するファイルの情報
    :type file_create: files_schemas.FileCreate
    :param uid: ファイルを所有するユーザーのID
    :type uid: str
    :return: 作成されたファイルのインスタンス
    :rtype: files_models.File
    """
    file_data = file_create.model_dump()
    file_data["user_id"] = uid
    file = files_models.File(**file_data)
    print(file)
    db.add(file)
    await db.commit()
    await db.refresh(file)
    return file


async def get_files_by_user_id(db: AsyncSession, uid: str) -> list[files_schemas.File]:
    """
    特定のユーザーに関連する全ファイルを取得する関数

    :param db: データベースセッション
    :type db: AsyncSession
    :param uid: ファイルを所有するユーザーのID
    :type uid: str
    :return: ファイルのリスト
    :rtype: list[files_schemas.File]
    """
    result: Result = await db.execute(
        select(files_models.File).filter(files_models.File.user_id == uid)
    )
    files = result.scalars().all()
    return [files_schemas.File.model_validate(file) for file in files]


async def get_file_by_id_and_user_id(
    db: AsyncSession, file_id: int, uid: str
) -> files_models.File | None:
    """
    ファイルIDとユーザーIDから特定のファイルを取得する関数

    :param db: データベースセッション
    :type db: AsyncSession
    :param file_id: 取得するファイルのID
    :type file_id: int
    :param uid: ファイルを所有するユーザーのID
    :type uid: str
    :return: 取得されたファイルのインスタンス、存在しない場合はNone
    :rtype: files_models.File | None
    """
    result: Result = await db.execute(
        select(files_models.File)
        .filter(files_models.File.id == file_id)
        .filter(files_models.File.user_id == uid)
    )
    return result.scalars().first()


async def delete_file_by_name_and_userid(db: AsyncSession, file_name: str, uid: str) -> None:
    """
    指定されたファイル名とユーザーIDに基づいてファイルを削除します。

    :param db: データベースセッション
    :type db: AsyncSession
    :param file_name: 削除するファイルの名前
    :type file_name: str
    :param uid: ファイルを所有するユーザーのID
    :type uid: str
    :return: None
    :rtype: None
    """
    result: Result = await db.execute(
        select(files_models.File)
        .filter(files_models.File.file_name == file_name)
        .filter(files_models.File.user_id == uid)
    )
    for file in result.scalars():
        await db.delete(file)
    await db.commit()


async def get_file_id_by_name_and_userid(db: AsyncSession, file_name: str, uid: str) -> int | None:
    """
    ファイル名とユーザーIDからファイルIDを取得する関数

    :param db: データベースセッション
    :type db: AsyncSession
    :param file_name: 取得するファイルの名前
    :type file_name: str
    :param uid: ファイルを所有するユーザーのID
    :type uid: str
    :return: ファイルID、存在しない場合はNone
    :rtype: int | None
    """
    result: Result = await db.execute(
        select(files_models.File.id)
        .filter(files_models.File.file_name == file_name)
        .filter(files_models.File.user_id == uid)
    )
    file = result.scalar_one_or_none()
    return file


# ファイルを更新する処理
async def update_file(
    db: AsyncSession, file_id: int, file_update: files_schemas.FileUpdate, uid: str
) -> files_models.File | None:
    """
    ファイルを更新する関数

    :param db: データベースセッション
    :type db: AsyncSession
    :param file_id: 更新するファイルのID
    :type file_id: int
    :param file_update: 更新するファイルの情報
    :type file_update: files_schemas.FileUpdate
    :param uid: ファイルを所有するユーザーのID
    :type uid: str
    :return: 更新されたファイルのインスタンス
    :rtype: files_models.File
    """
    result: Result = await db.execute(
        select(files_models.File)
        .filter(files_models.File.id == file_id)
        .filter(files_models.File.user_id == uid)
    )
    print(result)
    file = result.scalars().first()
    file_data = file_update.model_dump()
    for key, value in file_data.items():
        setattr(file, key, value)
    await db.commit()
    await db.refresh(file)
    return file
