import logging

from fastapi import APIRouter, HTTPException
from google.api_core.exceptions import GoogleAPIError, InvalidArgument, NotFound

from app.utils.gemini_request import generate_content

# ロギング設定
logging.basicConfig(level=logging.INFO)


# ルーターの設定
router = APIRouter(
    prefix="/outputs",
    tags=["outputs"],
)


# 複数のファイル名のリストを入力して、出力を生成するエンドポイント
@router.post("/request", response_model=str)
async def request_content(files: list[str]) -> str:
    # ロギング
    logging.info(f"Requesting content generation for files: {files}")

    # ファイル名のリストを取得
    file_names = files

    try:
        # ファイル名のリストを元に、コンテンツを生成
        content = generate_content(file_names)
    except NotFound as e:
        logging.error(f"File not found in Google Cloud Storage: {e}")
        raise HTTPException(
            status_code=404,
            detail="指定されたファイルがGoogle Cloud Storageに見つかりません。ファイル名を再確認してください。",
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

    return content
