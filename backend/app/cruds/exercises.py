import logging

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import app.models.exercises as exercises_models
import app.models.exercises_user_answer as exercises_user_answer_models
import app.models.files as files_models
import app.schemas.exercises as exercises_schemas
import app.schemas.exercises_user_answer as exercises_user_answer_schemas


async def create_exercise(
    db: AsyncSession, exercise_create: exercises_schemas.ExerciseCreate
) -> exercises_models.Exercise:
    """
    新しい練習問題を作成する関数。
    ExerciseCreateスキーマには既にuser_idが含まれているため、追加のユーザーIDは不要です。

    :param db: データベースセッション
    :type db: AsyncSession
    :param exercise_create: 作成する練習問題の情報（user_idを含む）
    :type exercise_create: exercises_schemas.ExerciseCreate
    :return: 作成された練習問題の情報
    :rtype: exercises_models.Exercise
    """
    # ExerciseCreateからファイル名を取り出し、残りのデータでExerciseを作成
    exercise_data = exercise_create.model_dump(exclude={"file_names"})
    exercise = exercises_models.Exercise(**exercise_data)

    # 先にexerciseを保存してIDを取得
    db.add(exercise)
    await db.flush()

    # ファイル名からファイルを取得して関連付け
    if exercise_create.file_names:
        files_result: Result = await db.execute(
            select(files_models.File).filter(
                files_models.File.file_name.in_(exercise_create.file_names)
            )
        )
        files = files_result.scalars().all()
        exercise.files.extend(files)

    await db.commit()
    await db.refresh(exercise)
    return exercise


async def get_exercises_by_user(
    db: AsyncSession, user_id: str
) -> list[exercises_schemas.ExerciseRead]:
    """
    ユーザーIDに基づいて練習問題を取得する関数。
    関連するファイル情報も含めて取得し、作成日時の降順でソートします。

    :param db: データベースセッション
    :type db: AsyncSession
    :param user_id: ユーザーID（Firebase UID）
    :type user_id: str
    :return: ユーザーに関連付けられた練習問題のリスト
    :rtype: list[exercises_schemas.ExerciseRead]
    :raises SQLAlchemyError: データベース操作中にエラーが発生した場合
    """
    try:
        result: Result = await db.execute(
            select(exercises_models.Exercise)
            .options(selectinload(exercises_models.Exercise.files))
            .filter(exercises_models.Exercise.user_id == user_id)
            .order_by(exercises_models.Exercise.created_at.desc())
        )
        exercises = result.scalars().all()
        return [exercises_schemas.ExerciseRead.model_validate(exercise) for exercise in exercises]

    except SQLAlchemyError as e:
        logging.error(f"Error retrieving exercises for user {user_id}: {e}")
        raise


async def get_exercise_by_id_and_user(
    db: AsyncSession, exercise_id: int, user_id: str
) -> exercises_models.Exercise | None:
    """
    練習問題IDとユーザーIDから特定の練習問題を取得する関数

    :param db: データベースセッション
    :type db: AsyncSession
    :param exercise_id: 取得する練習問題のID
    :type exercise_id: int
    :param user_id: ユーザーID（Firebase UID）
    :type user_id: str
    :return: 練習問題の情報またはNone
    :rtype: exercises_models.Exercise | None
    :raises SQLAlchemyError: データベース操作中にエラーが発生した場合
    """
    try:
        result: Result = await db.execute(
            select(exercises_models.Exercise)
            .options(selectinload(exercises_models.Exercise.files))
            .filter(exercises_models.Exercise.id == exercise_id)
            .filter(exercises_models.Exercise.user_id == user_id)
        )
        return result.scalars().first()

    except SQLAlchemyError as e:
        logging.error(f"Error retrieving exercise {exercise_id} for user {user_id}: {e}")
        raise


async def delete_exercise_by_user(
    db: AsyncSession, original_exercise: exercises_models.Exercise, user_id: str
) -> None:
    """
    ユーザーIDと練習問題の情報から特定の練習問題を削除する関数

    :param db: データベースセッション
    :type db: AsyncSession
    :param original_exercise: 削除する練習問題の情報
    :type original_exercise: exercises_models.Exercise
    :param user_id: ユーザーID（Firebase UID）
    :type user_id: str
    :return: None
    :rtype: None
    :raises ValueError: 指定されたユーザーが練習問題の所有者でない場合
    :raises SQLAlchemyError: データベース操作中にエラーが発生した場合
    """
    try:
        # ユーザーIDの確認
        if original_exercise.user_id != user_id:
            raise ValueError("User is not authorized to delete this exercise")

        # cascade=Trueの設定により、中間テーブルのレコードも自動的に削除される
        await db.delete(original_exercise)
        await db.commit()
        return None

    except SQLAlchemyError as e:
        await db.rollback()
        logging.error(f"Error deleting exercise {original_exercise.id} for user {user_id}: {e}")
        raise


async def get_exercise_files_by_user(
    db: AsyncSession, exercise_id: int, user_id: str
) -> list[files_models.File]:
    """
    ユーザーIDと練習問題IDから関連付けられたファイルを取得する関数

    :param db: データベースセッション
    :type db: AsyncSession
    :param exercise_id: 練習問題ID
    :type exercise_id: int
    :param user_id: ユーザーID（Firebase UID）
    :type user_id: str
    :return: 関連付けられたファイルのリスト
    :rtype: list[files_models.File]
    :raises ValueError: 練習問題が見つからない場合、またはユーザーが権限を持っていない場合
    :raises SQLAlchemyError: データベース操作中にエラーが発生した場合
    """
    try:
        result: Result = await db.execute(
            select(exercises_models.Exercise)
            .options(selectinload(exercises_models.Exercise.files))
            .filter(exercises_models.Exercise.id == exercise_id)
            .filter(exercises_models.Exercise.user_id == user_id)
        )
        exercise = result.scalar_one_or_none()

        if exercise is None:
            raise ValueError(f"Exercise with ID {exercise_id} not found for user {user_id}")

        return exercise.files

    except SQLAlchemyError as e:
        logging.error(f"Error retrieving files for exercise {exercise_id} and user {user_id}: {e}")
        raise


async def create_user_answer(
    db: AsyncSession, user_answer_create: exercises_user_answer_schemas.ExerciseUserAnswerCreate
) -> exercises_user_answer_models.ExerciseUserAnswer:
    user_answer = exercises_user_answer_models.ExerciseUserAnswer(**user_answer_create.model_dump())
    db.add(user_answer)
    await db.commit()
    await db.refresh(user_answer)
    return user_answer
