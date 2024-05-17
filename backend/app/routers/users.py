from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import app.schemas.users as users_schemas
import app.cruds.users as users_cruds
from app.db import get_db


router = APIRouter()


@router.get("/users/", response_model=list[users_schemas.User], tags=["users"])
async def list_users(db: AsyncSession = Depends(get_db)):
    return await users_cruds.get_users(db)


@router.post("/users/", response_model=users_schemas.UserCreateResponse, tags=["users"])
async def create_user(user_body: users_schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    return await users_cruds.create_user(db, user_body)


@router.get("/users/{user_id}/", response_model=users_schemas.User, tags=["users"])
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await users_cruds.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}/", response_model=users_schemas.UserCreateResponse, tags=["users"])
async def update_user(
    user_id: int,
    user_body: users_schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
):
    user = await users_cruds.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return await users_cruds.update_user(db, user_body, original_user=user)


@router.delete("/users/{user_id}/", tags=["users"])
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await users_cruds.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return await users_cruds.delete_user(db, original_user=user)
