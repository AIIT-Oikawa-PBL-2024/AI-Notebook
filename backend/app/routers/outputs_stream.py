import asyncio
import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from google.api_core.exceptions import GoogleAPIError, InvalidArgument, NotFound

from app.utils.gemini_request_stream import generate_content_stream

# ロギング設定
logging.basicConfig(level=logging.INFO)

# ルーターの設定
router = APIRouter(
    prefix="/outputs",
    tags=["outputs"],
)


# 複数のファイル名のリストを入力して、出力を生成するエンドポイント
@router.post("/request_stream")
async def request_content(files: list[str]) -> StreamingResponse:
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

    # コンテンツをストリーミングする非同期関数
    async def content_streamer() -> AsyncGenerator[str, None]:
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
            # DBに登録するための処理を追加する
            # ここではログに出力するだけ
            logging.info(f"Final content for DB: {final_content}")

    # ストリーミングレスポンスを返す
    return StreamingResponse(content_streamer(), media_type="text/event-stream")
