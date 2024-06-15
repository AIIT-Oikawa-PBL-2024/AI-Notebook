from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

import app.cruds.users as users_cruds
import app.schemas.users as users_schemas
from app.database import get_db

router = APIRouter()

db_dependency = Depends(get_db)


# ルーターの設定
router = APIRouter(
    prefix="/users",
    tags=["users"],
)


# ユーザーの一覧を取得するエンドポイント
@router.get("/", response_model=list[users_schemas.User])
async def list_users(db: AsyncSession = db_dependency) -> list[users_schemas.User]:
    return await users_cruds.get_users(db)


# 新しいユーザーを作成するエンドポイント
@router.post(
    "/",
    response_model=users_schemas.UserCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_body: users_schemas.UserCreate, db: AsyncSession = db_dependency
) -> users_schemas.UserCreateResponse:
    return await users_cruds.create_user(db, user_body)


# ユーザーIDから特定のユーザーを取得するエンドポイント
@router.get("/{user_id}", response_model=users_schemas.User)
async def get_user(
    user_id: int, db: AsyncSession = db_dependency
) -> users_schemas.User:
    user = await users_cruds.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    return user


# ユーザーIDから特定のユーザーを削除するエンドポイント
@router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = db_dependency) -> dict:
    user = await users_cruds.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    await users_cruds.delete_user(db, user_id=user_id)  # 修正された行
    return {"detail": "ユーザーが削除されました"}
