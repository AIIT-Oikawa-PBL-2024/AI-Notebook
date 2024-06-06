from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

import app.models.users as users_models
import app.schemas.users as users_schemas


# 新しいユーザーを作成する関数
async def create_user(
    db: AsyncSession, user_create: users_schemas.UserCreate
) -> users_models.User:
    # ユーザーのインスタンスを作成
    user = users_models.User(**user_create.model_dump())
    db.add(user)  # ユーザーをデータベースに追加
    await db.commit()  # 変更をコミット
    await db.refresh(user)  # ユーザーの情報をリフレッシュ
    return user


# 全ユーザーを取得する関数
async def get_users(db: AsyncSession) -> list[users_schemas.User]:
    # ユーザー情報を選択
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
    # 指定されたユーザーIDのユーザー情報を選択
    result: Result = await db.execute(
        select(users_models.User).filter(users_models.User.id == user_id)
    )
    return result.scalars().first()  # 結果の最初のユーザーを返す


# ユーザーIDから特定のユーザーを削除する関数
async def delete_user(db: AsyncSession, user_id: int) -> None:
    # 指定されたユーザーIDのユーザー情報を選択
    result: Result = await db.execute(
        select(users_models.User).filter(users_models.User.id == user_id)
    )
    original_user = result.scalars().first()  # 結果の最初のユーザーを取得
    if original_user:
        await db.delete(original_user)  # ユーザーを削除
        await db.commit()  # 変更をコミット
    return
