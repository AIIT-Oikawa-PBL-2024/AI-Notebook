from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

import app.models.users as users_models
import app.schemas.users as users_schemas


# 新しいユーザーを作成する関数
async def create_user(
    db: AsyncSession, user_create: users_schemas.UserCreate
) -> users_models.User:
    """
    新しいユーザーを作成する

    :param db: データベースセッション
    :type db: AsyncSession
    :param user_create: 作成するユーザーのデータ
    :type user_create: users_schemas.UserCreate
    :return: 作成されたユーザー
    :rtype: users_models.User
    """
    user = users_models.User(**user_create.model_dump())
    db.add(user)  # ユーザーをデータベースに追加
    await db.commit()  # 変更をコミット
    await db.refresh(user)  # ユーザーの情報をリフレッシュ
    return user


# 全ユーザーを取得する関数
async def get_users(db: AsyncSession) -> list[users_schemas.User]:
    """
    全ユーザーを取得する

    :param db: データベースセッション
    :type db: AsyncSession
    :return: ユーザーのリスト
    :rtype: list[users_schemas.User]
    """
    result: Result = await db.execute(
        select(
            users_models.User.id,
            users_models.User.username,
            users_models.User.email,
        )
    )
    users = result.all()  # 結果を取得
    # ユーザー情報をスキーマに変換して返す
    return [
        users_schemas.User(id=user.id, username=user.username, email=user.email)
        for user in users
    ]


# ユーザーIDから特定のユーザーを取得する関数
async def get_user_by_id(db: AsyncSession, user_id: int) -> users_models.User | None:
    """
    ユーザーIDから特定のユーザーを取得する

    :param db: データベースセッション
    :type db: AsyncSession
    :param user_id: 取得するユーザーのID
    :type user_id: int
    :return: ユーザー情報、存在しない場合はNone
    :rtype: users_models.User | None
    """
    result: Result = await db.execute(
        select(users_models.User).filter(users_models.User.id == user_id)
    )
    return result.scalars().first()  # 結果の最初のユーザーを返す


# ユーザーIDから特定のユーザーを削除する関数
async def delete_user(db: AsyncSession, user_id: int) -> None:
    """
    ユーザーIDから特定のユーザーを削除する

    :param db: データベースセッション
    :type db: AsyncSession
    :param user_id: 削除するユーザーのID
    :type user_id: int
    :return: なし
    :rtype: None
    """
    result: Result = await db.execute(
        select(users_models.User).filter(users_models.User.id == user_id)
    )
    original_user = result.scalars().first()  # 結果の最初のユーザーを取得
    if original_user:
        await db.delete(original_user)  # ユーザーを削除
        await db.commit()  # 変更をコミット
    return
