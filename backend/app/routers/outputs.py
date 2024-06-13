import logging
import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from google.api_core.exceptions import GoogleAPIError, InvalidArgument, NotFound
from sqlalchemy.ext.asyncio import AsyncSession

import app.cruds.outputs as outputs_cruds
import app.schemas.outputs as outputs_schemas
from app.database import get_db
from app.utils.gemini_request import generate_content

# 環境変数を読み込む
load_dotenv()

# ロギング設定
logging.basicConfig(level=logging.INFO)

# 環境変数から認証情報を取得
BUCKET_NAME: str = str(os.getenv("BUCKET_NAME"))

# ルーターの設定
router = APIRouter(
    prefix="/outputs",
    tags=["outputs"],
)


# 日本時間のタイムゾーン
JST = timezone(timedelta(hours=9))

# 依存関係
db_dependency = Depends(get_db)


# 学習帳のDB登録
@router.post("/upload", response_model=outputs_schemas.Output)
async def upload_outputs(
    outputs: outputs_schemas.Output,
    db: AsyncSession = db_dependency,
) -> outputs_schemas.Output:
    uploaded_output: outputs_schemas.Output

    if outputs.output:
        # 日本時間の現在日時を取得
        now_japan = datetime.now(JST)

        output_create = outputs_schemas.OutputCreate(
            output=outputs.output,
            user_id=1,  # ユーザIDは仮で1を設定
            created_at=now_japan,  # 日本時間の現在日時を設定
        )

        # 学習帳を保存
        uploaded_output = await outputs_cruds.create_output(db, output_create)
        logging.info(f"Output {outputs.output} saved to database.")

    return uploaded_output


# 学習帳の一覧取得
@router.get("/", response_model=list[outputs_schemas.Output])
async def get_outputs(db: AsyncSession = db_dependency) -> list[outputs_schemas.Output]:
    return await outputs_cruds.get_outputs(db)


# 学習帳の取得
@router.get("/{output_id}", response_model=outputs_schemas.Output)
async def get_output_by_id(
    output_id: int, db: AsyncSession = db_dependency
) -> outputs_schemas.Output:
    output = await outputs_cruds.get_output_by_id(db, output_id)
    if not output:
        raise HTTPException(status_code=404, detail="学習帳が見つかりません")
    return output


# 学習帳の削除
@router.delete("/{output_id}", response_model=dict)
async def delete_output(output_id: int, db: AsyncSession = db_dependency) -> dict:
    output = await outputs_cruds.get_output_by_id(db, output_id)
    if not output:
        raise HTTPException(status_code=404, detail="学習帳が見つかりません")
    await outputs_cruds.delete_output(db, output)
    return {"detail": "学習帳が削除されました"}


# 複数のファイル名のリストを入力して、出力を生成するエンドポイント
@router.post("/request", response_model=str)
async def request_content(
    files: list[str],
    db: AsyncSession = db_dependency,
) -> str:
    # ロギング
    logging.info(f"Requesting content generation for files: {files}")

    # ファイル名のリストを取得
    file_names = files

    try:
        # ファイル名のリストを元に、コンテンツを生成
        content = await generate_content(file_names)

        # DBに登録するための処理
        if content:
            # 日本時間の現在日時を取得
            now_japan = datetime.now(JST)

            output_create = outputs_schemas.OutputCreate(
                output=content,
                user_id=1,  # ユーザIDは仮で1を設定
                created_at=now_japan,  # 日本時間の現在日時を設定
            )

            # 学習帳を保存
            await outputs_cruds.create_output(db, output_create)
            await db.commit()
            logging.info("Output markdown saved to database.")

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

    return content
