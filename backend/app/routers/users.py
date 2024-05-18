from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import app.cruds.users as users_cruds
import app.schemas.users as users_schemas
from app.db import get_db

router = APIRouter()

db_dependency = Depends(get_db)


@router.get("/users/", response_model=List[users_schemas.User], tags=["users"])
async def list_users(db: AsyncSession = db_dependency) -> List[users_schemas.User]:
    return await users_cruds.get_users(db)


@router.post("/users/", response_model=users_schemas.UserCreateResponse, tags=["users"])
async def create_user(
    user_body: users_schemas.UserCreate, db: AsyncSession = db_dependency
) -> users_schemas.UserCreateResponse:
    return await users_cruds.create_user(db, user_body)


@router.get("/users/{user_id}/", response_model=users_schemas.User, tags=["users"])
async def get_user(
    user_id: int, db: AsyncSession = db_dependency
) -> users_schemas.User:
    user = await users_cruds.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/users/{user_id}/", tags=["users"])
async def delete_user(user_id: int, db: AsyncSession = db_dependency) -> dict:
    user = await users_cruds.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    await users_cruds.delete_user(db, original_user=user)
    return {"detail": "User deleted successfully"}
