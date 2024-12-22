import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from google.api_core.exceptions import GoogleAPIError, InvalidArgument, NotFound
from pydantic import ValidationError
from sqlalchemy import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import app.cruds.exercises as exercises_cruds
import app.models.exercises as exercises_models
import app.schemas.exercises as exercises_schemas
import app.schemas.exercises_user_answer as exercises_user_answer_schemas
from app.cruds.files import get_file_id_by_name_and_userid
from app.database import get_db
from app.models.exercises_files import exercise_file
from app.utils.claude_request_stream import generate_content_stream
from app.utils.essay_question import generate_essay_json
from app.utils.multiple_choice_question import generate_content_json
from app.utils.user_answer import generate_scoring_result_json
from app.utils.user_auth import get_uid

# ロギング設定
logging.basicConfig(level=logging.INFO)

# ルーターの設定
router = APIRouter(
    prefix="/exercises",
    tags=["exercises"],
)

# 日本時間のタイムゾーン
JST = timezone(timedelta(hours=9))

# 依存関係
db_dependency = Depends(get_db)


@router.post("/request_stream")
async def request_content(
    request: exercises_schemas.ExerciseRequest,
    uid: str = Depends(get_uid),
    db: AsyncSession = db_dependency,
) -> StreamingResponse:
    """
    複数のファイル名のリストを入力して、コンテンツをストリーミングするエンドポイント

    このエンドポイントは、ユーザーが提供したファイル名のリストに基づいて、対応するコンテンツを
    生成し、ストリーミング形式で返却します。ファイル名とユーザーIDからデータベース内の
    ファイルIDを取得し、対応するコンテンツを生成します。生成したコンテンツはリアルタイムで
    ストリーミングされ、最終的なコンテンツはデータベースに保存されます。

    :param files: コンテンツ生成のために必要なファイル名のリスト
    :type files: list[str]
    :param title: コンテンツのタイトル
    :type title: str
    :param uid: 現在のユーザーのID（Firebase UID）
    :type uid: str
    :param db: 非同期データベースセッション
    :type db: AsyncSession
    :return: コンテンツをストリーミングするStreamingResponse
    :rtype: StreamingResponse
    :raises HTTPException: コンテンツ生成中に予期せぬエラーが発生した場合
    """
    logging.info(f"Requesting content generation for files: {request.files} by user: {uid}")

    # ユーザーIDとファイル名から関連するファイルIDを取得
    file_ids = []
    missing_files = []

    for file_name in request.files:
        try:
            logging.info(f"Attempting to retrieve file ID for file_name: {file_name}")
            file_id = await get_file_id_by_name_and_userid(db, file_name, uid)
            if file_id is None:
                logging.warning(
                    f"File not found in database for file_name: {file_name} and user_id: {uid}"
                )
                missing_files.append(file_name)
            else:
                logging.info(f"Found file ID: {file_id} for file_name: {file_name}")
                file_ids.append(file_id)
        except Exception as e:
            logging.error(f"Error retrieving file ID for file_name: {file_name}: {e}")
            raise HTTPException(
                status_code=500,
                detail="データベースからファイル情報を取得する際にエラーが発生しました。",
            ) from e

    if missing_files:
        raise HTTPException(
            status_code=404,
            detail="指定されたファイルの一部がデータベースに存在しません:"
            + f" {', '.join(missing_files)}",
        )

    # コンテンツ生成ストリームの開始
    try:
        logging.info("Starting content generation stream...")
        response = generate_content_stream(request.files, uid)
    except NotFound as e:
        logging.error(f"File not found in Google Cloud Storage: {e}")
        raise HTTPException(
            status_code=404,
            detail="指定されたファイルがGoogle Cloud Storageに見つかりません。"
            + "ファイル名を再確認してください。",
        ) from e
    except InvalidArgument as e:
        logging.error(f"Invalid argument: {e}")
        raise HTTPException(
            status_code=400,
            detail="ファイル名の形式が無効です。有効なファイル名を指定してください。",
        ) from e
    except GoogleAPIError as e:
        logging.error(f"Google API error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Google APIからエラーが返されました。システム管理者に連絡してください。",
        ) from e
    except Exception as e:
        logging.error(f"Error generating content: {e}")
        raise HTTPException(
            status_code=500,
            detail="コンテンツの生成中に予期せぬエラーが発生しました。システム管理者に連絡してください。",
        ) from e

    async def content_streamer() -> AsyncGenerator[str, None]:
        """
        コンテンツをストリーミングする非同期ジェネレータ関数

        この関数は、生成されたコンテンツをリアルタイムでストリーミングするための
        非同期ジェネレータです。コンテンツの一部が生成されるたびに、ストリーミングレスポンス
        に送信され、最終的なコンテンツはデータベースに保存されます。

        :return: ストリーミングされるコンテンツ
        :rtype: AsyncGenerator[str, None]
        """
        accumulated_content = []

        try:
            async for content in response:
                # contentがbytes型であればデコードし、str型であればそのまま利用
                if isinstance(content, bytes):
                    content = content.decode("utf-8")
                logging.info(f"Streaming content: {content}")
                accumulated_content.append(content)
                yield content
                await asyncio.sleep(0.05)

        except asyncio.CancelledError:
            logging.warning("ストリーミングがキャンセルされました。")
            raise

        # 最終コンテンツの保存
        final_content = "".join(accumulated_content)
        if final_content:
            try:
                logging.info("Saving final content to database.")
                exercise = exercises_models.Exercise(
                    title=request.title,
                    response=final_content,
                    user_id=uid,
                    created_at=datetime.now(JST),
                    exercise_type="stream",
                )

                db.add(exercise)
                await db.flush()  # exercise.idを取得するため一旦flushします

                # 中間テーブルへの関連付けを手動で追加
                # 複数のファイルIDを関連付ける
                for file_id in file_ids:
                    await db.execute(
                        insert(exercise_file).values(exercise_id=exercise.id, file_id=file_id)
                    )

                await db.commit()
                await db.refresh(exercise)
                logging.info(f"Exercise saved to database with ID: {exercise.id}")

            except Exception as e:
                logging.error(f"Error saving exercise to database: {e}")
                raise HTTPException(
                    status_code=500,
                    detail="コンテンツをデータベースに保存中にエラーが発生しました。システム管理者に連絡してください。",
                ) from e

    return StreamingResponse(content_streamer(), media_type="text/event-stream")


@router.post("/multiple_choice")
async def request_choice_question_json(
    request: exercises_schemas.ExerciseRequest,
    uid: str = Depends(get_uid),
    db: AsyncSession = db_dependency,
) -> dict:
    """
    複数のファイル名のリストを入力して、選択問題を生成するエンドポイント

    :param files: 選択問題生成のためのファイル名リスト
    :type files: list[str]
    :param title: 選択問題のタイトル
    :type title: str
    :param uid: 現在のユーザーのID（Firebase UID）
    :type uid: str
    :param db: 非同期データベースセッション
    :type db: AsyncSession
    :return: 生成された選択問題のJSONデータ
    :rtype: dict
    :raises HTTPException: 生成中にエラーが発生した場合
    """
    logging.info(f"Requesting content generation for files: {request.files}")

    # ユーザーIDとファイル名から関連するファイルIDを取得
    file_ids = []
    missing_files = []

    for file_name in request.files:
        try:
            logging.info(f"Attempting to retrieve file ID for file_name: {file_name}")
            file_id = await get_file_id_by_name_and_userid(db, file_name, uid)
            if file_id is None:
                logging.warning(
                    f"File not found in database for file_name: {file_name} and user_id: {uid}"
                )
                missing_files.append(file_name)
            else:
                logging.info(f"Found file ID: {file_id} for file_name: {file_name}")
                file_ids.append(file_id)
        except Exception as e:
            logging.error(f"Error retrieving file ID for file_name: {file_name}: {e}")
            raise HTTPException(
                status_code=500,
                detail="データベースからファイル情報を取得する際にエラーが発生しました。",
            ) from e

    if missing_files:
        raise HTTPException(
            status_code=404,
            detail="指定されたファイルの一部がデータベースに存在しません:"
            + f" {', '.join(missing_files)}",
        )

    try:
        response = await generate_content_json(
            files=request.files,
            uid=uid,
            title=request.title,  # タイトルを追加
        )
        logging.info(f"Generated response: {response}")
    except NotFound as e:
        logging.error(f"File not found in Google Cloud Storage: {e}")
        raise HTTPException(
            status_code=404,
            detail="指定されたファイルがGoogle Cloud Storageに見つかりません。"
            + "ファイル名を再確認してください。",
        ) from e
    except InvalidArgument as e:
        logging.error(f"Invalid argument: {e}")
        raise HTTPException(
            status_code=400,
            detail="ファイル名の形式が無効です。有効なファイル名を指定してください。",
        ) from e
    except GoogleAPIError as e:
        logging.error(f"Google API error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Google APIからエラーが返されました。システム管理者に連絡してください。",
        ) from e
    except Exception as e:
        logging.error(f"Error generating content: {e}")
        raise HTTPException(
            status_code=500,
            detail="コンテンツの生成中に予期せぬエラーが発生しました。システム管理者に連絡してください。",
        ) from e

    if response:
        try:
            logging.info("Saving final content to database.")
            # Exerciseインスタンスを作成し、exerciseファイルの関連付けは直接行う
            exercise = exercises_models.Exercise(
                title=request.title,
                response=json.dumps(response),
                user_id=uid,
                created_at=datetime.now(JST),
                exercise_type="multiple_choice",
            )

            db.add(exercise)
            await db.flush()  # exercise.idを取得するため一旦flushします

            # 中間テーブルへの関連付けを手動で追加
            for file_id in file_ids:
                await db.execute(
                    insert(exercise_file).values(exercise_id=exercise.id, file_id=file_id)
                )

            await db.commit()
            await db.refresh(exercise)
            logging.info(f"Exercise saved to database with ID: {exercise.id}")

        except Exception as e:
            logging.error(f"Error saving exercise to database: {e}")
            raise HTTPException(
                status_code=500,
                detail="コンテンツをデータベースに保存中にエラーが発生しました。システム管理者に連絡してください。",
            ) from e

    return response


@router.get("/list", response_model=list[exercises_schemas.ExerciseRead])
async def list_exercises(
    uid: str = Depends(get_uid),
    db: AsyncSession = db_dependency,
) -> list[exercises_schemas.ExerciseRead]:
    """
    ユーザーの練習問題一覧を取得するエンドポイント。
    ユーザーIDに基づいて、そのユーザーに関連付けられた全ての練習問題を取得し、
    関連するファイル情報と共に返します。

    :param uid: 現在のユーザーのID（Firebase UID）
    :type uid: str
    :param db: 非同期データベースセッション
    :type db: AsyncSession
    :return: ユーザーに関連付けられた練習問題のリスト。各練習問題には関連ファイル情報が含まれます。
    :rtype: list[exercises_schemas.ExerciseRead]
    :raises HTTPException: データベースの操作やデータの検証中にエラーが発生した場合
    """
    try:
        exercises = await exercises_cruds.get_exercises_by_user(db, uid)
        logging.info(f"Retrieved {len(exercises)} exercises for user {uid}")
        return exercises

    except ValidationError as ve:
        logging.error(f"Validation error while processing exercises: {ve}")
        raise HTTPException(
            status_code=422,
            detail="データの検証中にエラーが発生しました。データ形式を確認してください。",
        ) from ve

    except SQLAlchemyError as se:
        logging.error(f"Database error while retrieving exercises: {se}")
        raise HTTPException(
            status_code=500,
            detail="データベースの操作中にエラーが発生しました。システム管理者に連絡してください。",
        ) from se

    except Exception as e:
        logging.error(f"Unexpected error while retrieving exercises: {e}")
        raise HTTPException(
            status_code=500,
            detail="練習問題の取得中に予期せぬエラーが発生しました。システム管理者に連絡してください。",
        ) from e


@router.get("/{exercise_id}", response_model=exercises_schemas.ExerciseRead)
async def get_exercise(
    exercise_id: int,
    uid: str = Depends(get_uid),
    db: AsyncSession = db_dependency,
) -> exercises_schemas.ExerciseRead:
    """
    特定の練習問題の詳細を取得するエンドポイント

    :param exercise_id: 取得する練習問題のID
    :type exercise_id: int
    :param uid: 現在のユーザーのID（Firebase UID）
    :type uid: str
    :param db: 非同期データベースセッション
    :type db: AsyncSession
    :return: 練習問題の詳細
    :rtype: exercises_schemas.ExerciseRead
    :raises HTTPException: 指定された練習問題が存在しない場合やアクセス権がない場合
    """
    try:
        exercise = await exercises_cruds.get_exercise_by_id_and_user(db, exercise_id, uid)
        if exercise is None:
            raise HTTPException(status_code=404, detail="指定された練習問題が見つかりません。")

        logging.info(f"Retrieved exercise {exercise_id} for user {uid}")
        return exercises_schemas.ExerciseRead.model_validate(exercise)

    except SQLAlchemyError as se:
        logging.error(f"Database error while retrieving exercise {exercise_id}: {se}")
        raise HTTPException(
            status_code=500,
            detail="データベースの操作中にエラーが発生しました。システム管理者に連絡してください。",
        ) from se

    except Exception as e:
        logging.error(f"Error retrieving exercise {exercise_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="練習問題の取得中にエラーが発生しました。システム管理者に連絡してください。",
        ) from e


@router.delete("/{exercise_id}", response_model=None)
async def delete_exercise_endpoint(
    exercise_id: int,
    uid: str = Depends(get_uid),
    db: AsyncSession = db_dependency,
) -> None:
    """
    特定の練習問題を削除するエンドポイント

    :param exercise_id: 削除する練習問題のID
    :type exercise_id: int
    :param uid: 現在のユーザーのID（Firebase UID）
    :type uid: str
    :param db: 非同期データベースセッション
    :type db: AsyncSession
    :return: None
    :raises HTTPException: 練習問題が存在しない場合やアクセス権がない場合
    """
    try:
        exercise = await exercises_cruds.get_exercise_by_id_and_user(db, exercise_id, uid)
        if exercise is None:
            raise HTTPException(status_code=404, detail="指定された練習問題が見つかりません。")

        await exercises_cruds.delete_exercise_by_user(db, exercise, uid)
        logging.info(f"Deleted exercise {exercise_id} for user {uid}")

    except ValueError as ve:
        logging.error(f"Authorization error while deleting exercise {exercise_id}: {ve}")
        raise HTTPException(
            status_code=403, detail="この練習問題を削除する権限がありません。"
        ) from ve

    except SQLAlchemyError as se:
        logging.error(f"Database error while deleting exercise {exercise_id}: {se}")
        raise HTTPException(
            status_code=500,
            detail="データベースの操作中にエラーが発生しました。システム管理者に連絡してください。",
        ) from se

    except Exception as e:
        logging.error(f"Error deleting exercise {exercise_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="練習問題の削除中にエラーが発生しました。システム管理者に連絡してください。",
        ) from e


@router.post("/essay_question")
async def request_essay_question_json(
    request: exercises_schemas.ExerciseRequest,
    uid: str = Depends(get_uid),
    db: AsyncSession = db_dependency,
) -> dict:
    """
    複数のファイル名のリストを入力して、記述問題を生成するエンドポイント

    :param files: 記述問題生成のためのファイル名リスト
    :type files: list[str]
    :param title: 記述問題のタイトル
    :type title: str
    :param uid: 現在のユーザーのID（Firebase UID）
    :type uid: str
    :param db: 非同期データベースセッション
    :type db: AsyncSession
    :return: 生成された記述問題のJSONデータ
    :rtype: dict
    :raises HTTPException: 生成中にエラーが発生した場合
    """
    logging.info(f"Requesting content generation for files: {request.files}")

    # ユーザーIDとファイル名から関連するファイルIDを取得
    file_ids = []
    missing_files = []

    for file_name in request.files:
        try:
            logging.info(f"Attempting to retrieve file ID for file_name: {file_name}")
            file_id = await get_file_id_by_name_and_userid(db, file_name, uid)
            if file_id is None:
                logging.warning(
                    f"File not found in database for file_name: {file_name} and user_id: {uid}"
                )
                missing_files.append(file_name)
            else:
                logging.info(f"Found file ID: {file_id} for file_name: {file_name}")
                file_ids.append(file_id)
        except Exception as e:
            logging.error(f"Error retrieving file ID for file_name: {file_name}: {e}")
            raise HTTPException(
                status_code=500,
                detail="データベースからファイル情報を取得する際にエラーが発生しました。",
            ) from e

    if missing_files:
        raise HTTPException(
            status_code=404,
            detail="指定されたファイルの一部がデータベースに存在しません:"
            + f" {', '.join(missing_files)}",
        )

    try:
        response = await generate_essay_json(
            files=request.files,
            uid=uid,
            title=request.title,  # タイトルを追加
        )
        logging.info(f"Generated response: {response}")
    except NotFound as e:
        logging.error(f"File not found in Google Cloud Storage: {e}")
        raise HTTPException(
            status_code=404,
            detail="指定されたファイルがGoogle Cloud Storageに見つかりません。"
            + "ファイル名を再確認してください。",
        ) from e
    except InvalidArgument as e:
        logging.error(f"Invalid argument: {e}")
        raise HTTPException(
            status_code=400,
            detail="ファイル名の形式が無効です。有効なファイル名を指定してください。",
        ) from e
    except GoogleAPIError as e:
        logging.error(f"Google API error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Google APIからエラーが返されました。システム管理者に連絡してください。",
        ) from e
    except Exception as e:
        logging.error(f"Error generating content: {e}")
        raise HTTPException(
            status_code=500,
            detail="コンテンツの生成中に予期せぬエラーが発生しました。システム管理者に連絡してください。",
        ) from e

    if response:
        try:
            logging.info("Saving final content to database.")
            # Exerciseインスタンスを作成し、exerciseファイルの関連付けは直接行う
            exercise = exercises_models.Exercise(
                title=request.title,
                response=json.dumps(response),
                user_id=uid,
                created_at=datetime.now(JST),
                exercise_type="essay_question",
            )

            db.add(exercise)
            await db.flush()  # exercise.idを取得するため一旦flushします

            # 中間テーブルへの関連付けを手動で追加
            for file_id in file_ids:
                await db.execute(
                    insert(exercise_file).values(exercise_id=exercise.id, file_id=file_id)
                )

            await db.commit()
            await db.refresh(exercise)
            logging.info(f"Exercise saved to database with ID: {exercise.id}")

            # exercise_idをresponseに追加
            response["exercise_id"] = exercise.id

        except Exception as e:
            logging.error(f"Error saving exercise to database: {e}")
            raise HTTPException(
                status_code=500,
                detail="コンテンツをデータベースに保存中にエラーが発生しました。システム管理者に連絡してください。",
            ) from e

    return response


@router.post("/user_answer")
async def create_user_answer(
    user_answer: exercises_user_answer_schemas.ExerciseUserAnswerRequest,
    uid: str = Depends(get_uid),
    db: AsyncSession = db_dependency,
) -> exercises_user_answer_schemas.ExerciseUserAnswerRead:
    """
    ユーザーの回答を作成するエンドポイント。

    :param user_answer: ユーザーの回答情報
    :type user_answer: exercises_schemas.ExerciseUserAnswerCreate
    :param uid: 現在のユーザーのID（Firebase UID）
    :type uid: str
    :param db: 非同期データベースセッション
    :type db: AsyncSession
    :return: 作成されたユーザーの回答情報
    :rtype: exercises_schemas.ExerciseUserAnswerRead
    :raises HTTPException: ユーザーの回答作成中にエラーが発生した場合
    """
    try:
        # exercise_idとuser_idからExerciseを取得
        exercise = await exercises_cruds.get_exercise_by_id_and_user(
            db, user_answer.exercise_id, uid
        )
        if exercise is None:
            raise HTTPException(status_code=404, detail="指定された練習問題が見つかりません。")

        # logging.info(f"Retrieved exercise {exercise.response} for user {uid}")

        response = await generate_scoring_result_json(
            exercise=exercise.response
            if isinstance(exercise.response, str)
            else str(exercise.response),
            user_answers=user_answer.user_answer,
            uid=uid,
        )
        logging.info(f"Generated response: {response}")

        # user_answer.user_answerをstringに変換
        user_answer_str = json.dumps(user_answer.user_answer)

        # ユーザーの回答と採点結果をデータベースに保存
        user_answer_db = exercises_user_answer_schemas.ExerciseUserAnswerCreate(
            exercise_id=user_answer.exercise_id,
            user_id=uid,
            answer=user_answer_str,
            scoring_results=json.dumps(response),
            created_at=datetime.now(JST),
        )
        user_answer_result = await exercises_cruds.create_user_answer(db, user_answer_db)
        return user_answer_result

    except ValidationError as ve:
        logging.error(f"Validation error while creating user answer: {ve}")
        raise HTTPException(
            status_code=422,
            detail="データの検証中にエラーが発生しました。データ形式を確認してください。",
        ) from ve

    except SQLAlchemyError as se:
        logging.error(f"Database error while creating user answer: {se}")
        raise HTTPException(
            status_code=500,
            detail="データベースの操作中にエラーが発生しました。システム管理者に連絡してください。",
        ) from se

    except Exception as e:
        logging.error(f"Error creating user answer: {e}")
        raise HTTPException(
            status_code=500,
            detail="ユーザーの回答作成中にエラーが発生しました。システム管理者に連絡してください。",
        ) from e
