from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

import app.models.users as users_models
import app.schemas.users as users_schemas


async def create_user(
    db: AsyncSession, user_create: users_schemas.UserCreate
) -> users_models.User:
    user = users_models.User(**user_create.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_users(db: AsyncSession) -> list[users_schemas.User]:
    result: Result = await db.execute(
        select(
            users_models.User.id,
            users_models.User.username,
            users_models.User.email,
        )
    )
    users = result.all()
    return [
        users_schemas.User(id=user.id, username=user.username, email=user.email)
        for user in users
    ]


async def get_user_by_id(db: AsyncSession, user_id: int) -> users_models.User | None:
    result: Result = await db.execute(
        select(users_models.User).filter(users_models.User.id == user_id)
    )
    return result.scalars().first()


async def delete_user(db: AsyncSession, original_user: users_models.User) -> None:
    await db.delete(original_user)
    await db.commit()
    return
