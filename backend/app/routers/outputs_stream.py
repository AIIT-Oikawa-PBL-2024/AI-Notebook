import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from google.api_core.exceptions import GoogleAPIError, InvalidArgument, NotFound
from sqlalchemy.ext.asyncio import AsyncSession

import app.cruds.outputs as outputs_cruds
import app.schemas.outputs as outputs_schemas
from app.database import get_db
from app.utils.gemini_request_stream import generate_content_stream

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
    files: list[str],
    db: AsyncSession = db_dependency,
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
    :raises HTTPException 500: コンテンツの生成中にエラーが発生した場合、またはGoogle APIからエラーが返された場合、またはコンテンツのストリーミング中にエラーが発生した場合
    """
    # ロギング
    logging.info(f"Requesting content generation for files: {files}")

    # ファイル名のリストを取得
    file_names = files

    try:
        # ファイル名のリストを元に、コンテンツを生成
        response = generate_content_stream(file_names)
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
            detail="Google APIからエラーが返されました。"
            + "システム管理者に連絡してください。",
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
                # 日本時間の現在日時を取得
                now_japan = datetime.now(JST)

                output_create = outputs_schemas.OutputCreate(
                    output=final_content,
                    user_id=1,  # ユーザIDは仮で1を設定
                    created_at=now_japan,  # 日本時間の現在日時を設定
                )

                # 学習帳を保存
                await outputs_cruds.create_output(db, output_create)
                await db.commit()
                logging.info("Output markdown saved to database.")

            # ログに出力
            logging.info(f"Final content for DB: {final_content}")

    # ストリーミングレスポンスを返す
    return StreamingResponse(content_streamer(), media_type="text/event-stream")
