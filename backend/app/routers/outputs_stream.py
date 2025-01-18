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

import app.cruds.outputs as outputs_cruds
import app.models.outputs as outputs_models
import app.schemas.outputs as outputs_schemas
from app.cruds.files import get_file_id_by_name_and_userid
from app.database import get_db
from app.models.outputs_files import output_file
from app.utils.gemini_request_stream import generate_content_stream
from app.utils.user_auth import get_uid

# ロギング設定
logging.basicConfig(level=logging.INFO)

# ルーターの設定
router = APIRouter(
    prefix="/outputs",
    tags=["outputs"],
)

# 日本時間のタイムゾーン
JST = timezone(timedelta(hours=9))

# 依存関係
db_dependency = Depends(get_db)


@router.post("/request_stream")
async def request_content(
    request: outputs_schemas.OutputRequest,
    db: AsyncSession = db_dependency,
    uid: str = Depends(get_uid),
) -> StreamingResponse:
    """
    ファイル名のリストを入力して、出力を生成するエンドポイントです。

    :param files: ファイル名のリスト
    :type files: list[str]
    :param db: 非同期セッション
    :type db: AsyncSession
    :return: ストリーミングレスポンス
    :rtype: StreamingResponse
    :raises HTTPException 404: 指定されたファイルが見つからない場合
    :raises HTTPException 400: ファイル名の形式が無効な場合
    :raises HTTPException 500: コンテンツの生成中にエラーが発生した場合、
                               またはGoogle APIからエラーが返された場合、
                               またはコンテンツのストリーミング中にエラーが発生した場合
    """
    # ロギング
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

    try:
        # ファイル名のリストを元に、コンテンツを生成
        response = generate_content_stream(request.files, uid, request.style)
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
            detail="Google APIからエラーが返されました。" + "システム管理者に連絡してください。",
        ) from e
    except Exception as e:
        logging.error(f"Error generating content: {e}")
        raise HTTPException(
            status_code=500,
            detail="コンテンツの生成中に予期せぬエラーが発生しました。"
            + "システム管理者に連絡してください。",
        ) from e

    async def content_streamer() -> AsyncGenerator[str, None]:
        """
        コンテンツをストリーミングする非同期関数です。

        :return: コンテンツのストリーム
        :rtype: AsyncGenerator[str, None]
        :raises HTTPException 500: コンテンツのストリーミング中にエラーが発生した場合
        """
        # コンテンツを蓄積するリスト
        accumulated_content = []
        try:
            async for content in response:
                # 辞書形式に変換
                content_dict = content.to_dict()

                # 辞書をJSON文字列に変換
                json_string = json.dumps(content_dict)

                # JSON文字列をパース
                data = json.loads(json_string)

                # textの値を取得して出力
                text_value = data["candidates"][0]["content"]["parts"][0]["text"]
                logging.info(f"Streaming content: {text_value}")
                accumulated_content.append(text_value)
                yield text_value
                await asyncio.sleep(0.05)

        except Exception as e:
            logging.error(f"Error while streaming content: {e}")
            raise HTTPException(
                status_code=500,
                detail="コンテンツのストリーミング中にエラーが発生しました。"
                + "システム管理者に連絡してください。",
            ) from e
        finally:
            # コンテンツを結合して1つの文字列にする
            final_content = "".join(accumulated_content)

            # DBに登録するための処理
            if final_content:
                try:
                    logging.info("Saving final content to database.")
                    output = outputs_models.Output(
                        title=request.title,
                        output=final_content,
                        user_id=uid,
                        created_at=datetime.now(JST),
                    )

                    db.add(output)
                    await db.flush()  # output.idを取得するため一旦flushします

                    # 中間テーブルへの関連付けを手動で追加
                    # 複数のファイルIDを関連付ける
                    for file_id in file_ids:
                        await db.execute(
                            insert(output_file).values(output_id=output.id, file_id=file_id)
                        )

                    await db.commit()
                    await db.refresh(output)
                    logging.info(f"Output saved to database with ID: {output.id}")

                except Exception as e:
                    logging.error(f"Error saving output to database: {e}")
                    raise HTTPException(
                        status_code=500,
                        detail="コンテンツをデータベースに保存中にエラーが発生しました。システム管理者に連絡してください。",
                    ) from e

            # ログに出力
            logging.info(f"Final content for DB: {final_content}")

    # ストリーミングレスポンスを返す
    return StreamingResponse(content_streamer(), media_type="text/event-stream")


@router.get("/list", response_model=list[outputs_schemas.OutputRead])
async def list_outputs(
    uid: str = Depends(get_uid),
    db: AsyncSession = db_dependency,
) -> list[outputs_schemas.OutputRead]:
    """
    ユーザーのAI出力一覧を取得するエンドポイント。
    ユーザーIDに基づいて、そのユーザーに関連付けられた全てのAI出力を取得し、
    関連するファイル情報と共に返します。

    :param uid: 現在のユーザーのID（Firebase UID）
    :type uid: str
    :param db: 非同期データベースセッション
    :type db: AsyncSession
    :return: ユーザーに関連付けられたAIのリスト。各AI出力には関連ファイル情報が含まれます。
    :rtype: list[outputs_schemas.OutputRead]
    :raises HTTPException: データベースの操作やデータの検証中にエラーが発生した場合
    """
    try:
        outputs = await outputs_cruds.get_outputs_by_user(db, uid)
        logging.info(f"Retrieved {len(outputs)} outputs for user {uid}")
        return outputs

    except ValidationError as ve:
        logging.error(f"Validation error while processing outputs: {ve}")
        raise HTTPException(
            status_code=422,
            detail="データの検証中にエラーが発生しました。データ形式を確認してください。",
        ) from ve

    except SQLAlchemyError as se:
        logging.error(f"Database error while retrieving outputs: {se}")
        raise HTTPException(
            status_code=500,
            detail="データベースの操作中にエラーが発生しました。システム管理者に連絡してください。",
        ) from se

    except Exception as e:
        logging.error(f"Unexpected error while retrieving outputs: {e}")
        raise HTTPException(
            status_code=500,
            detail="AI出力の取得中に予期せぬエラーが発生しました。システム管理者に連絡してください。",
        ) from e


@router.get("/{output_id}", response_model=outputs_schemas.OutputRead)
async def get_output(
    output_id: int,
    uid: str = Depends(get_uid),
    db: AsyncSession = db_dependency,
) -> outputs_schemas.OutputRead:
    """
    特定のAI出力の詳細を取得するエンドポイント

    :param output_id: 取得するAI出力のID
    :type output_id: int
    :param uid: 現在のユーザーのID（Firebase UID）
    :type uid: str
    :param db: 非同期データベースセッション
    :type db: AsyncSession
    :return: AI出力の詳細
    :rtype: outputs_schemas.OutputRead
    :raises HTTPException: 指定されたAI出力が存在しない場合やアクセス権がない場合
    """
    try:
        output = await outputs_cruds.get_output_by_id_and_user(db, output_id, uid)
        if output is None:
            raise HTTPException(status_code=404, detail="指定されたAI出力が見つかりません。")

        logging.info(f"Retrieved output {output_id}")
        return output

    except SQLAlchemyError as se:
        logging.error(f"Database error while retrieving output {output_id}: {se}")
        raise HTTPException(
            status_code=500,
            detail="データベースの操作中にエラーが発生しました。システム管理者に連絡してください。",
        ) from se

    except Exception as e:
        logging.error(f"Error retrieving output {output_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="AI出力の取得中にエラーが発生しました。システム管理者に連絡してください。",
        ) from e


@router.delete("/{output_id}", response_model=None)
async def delete_output_endpoint(
    output_id: int,
    uid: str = Depends(get_uid),
    db: AsyncSession = db_dependency,
) -> None:
    """
    特定のAI出力を削除するエンドポイント

    :param output_id: 削除するAI出力のID
    :type output_id: int
    :param uid: 現在のユーザーのID（Firebase UID）
    :type uid: str
    :param db: 非同期データベースセッション
    :type db: AsyncSession
    :return: None
    :raises HTTPException: AI出力が存在しない場合やアクセス権がない場合
    """
    try:
        output = await outputs_cruds.get_output_by_id_and_user(db, output_id, uid)
        if output is None:
            raise HTTPException(status_code=404, detail="指定されたAI出力が見つかりません。")

        await outputs_cruds.delete_output(db, output)
        logging.info(f"Deleted output {output_id}")

    except ValueError as ve:
        logging.error(f"Authorization error while deleting output {output_id}: {ve}")
        raise HTTPException(
            status_code=403, detail="このAI出力を削除する権限がありません。"
        ) from ve

    except SQLAlchemyError as se:
        logging.error(f"Database error while deleting output {output_id}: {se}")
        raise HTTPException(
            status_code=500,
            detail="データベースの操作中にエラーが発生しました。システム管理者に連絡してください。",
        ) from se

    except Exception as e:
        logging.error(f"Error deleting output {output_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="AI出力の削除中にエラーが発生しました。システム管理者に連絡してください。",
        ) from e
