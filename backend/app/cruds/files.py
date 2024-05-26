from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

import os
import app.models.files as file_models
import app.schemas.files as files_schemas

from google.cloud import storage
from fastapi import FastAPI, File, UploadFile, HTTPException

# 複数ファイルをリストで受け取って条件似合わないものがあればスルー
# ユーザは複数ファイルアップロード、Streamlitで1つずつ送る？
# 後々動画が入ってくることも考慮すべき
# クライアント側には一般的なエラー伝える
# gcsにあげる時にファイル名が被ってたら拒否
# 同じファイル名が上がったときに、エラーにするかバケットのファイル削除する？ -> 同じファイルだと上書きだが、警告出す（先にファイル情報をgetして一覧で出しておく）
# mypyの設定

async def post_files(file: UploadFile):
    allowed_extensions = [".png", ".pdf", ".jpeg", ".jpg"]
    file_extensions = os.path.splitext(file.filename)[1].lower()
# リストのファイルを確認して成功失敗を教える、失敗したファイルを教えてあげる

    # if file_extensions not in allowed_extensions:
    #     raise HTTPException(status_code=400, detail="無効なファイル拡張子です") 

    try:
        client = storage.Client() # Google Cloud Storageのクライアントを作成
        bucket = client.bucket(os.environ["GCS_BUCKET_NAME"])  # バケットを取得->環境変数にバケット名入れる
        file_name = file.filename  # ファイル名取得 -> バイナリとして取らないとダメなので、filename使えない？
        blob = bucket.blob(file_name)  # バケットにBlobを作成
        blob.upload_from_file(file.file)  # ファイルをアップロード
        return {"message": "ファイルのアップロードに成功しました -> 成功と失敗したファイルを教える"}

    except Exception as e:
        # エラーが発生した場合は、HTTPExceptionを発生させる
        raise HTTPException(status_code=500, detail=str(e))

async def post_filename_to_db(db: AsyncSession, file: UploadFile):
    # ファイル名をデータベースに保存
    db_file = file_models.File(file_name=file.filename)
    db.add(db_file)
    await db.commit()
    await db.refresh(db_file)
    return db_file

async def create_file(db: AsyncSession, file: UploadFile):
    # ファイルをGoogle Cloud Storageにアップロード
    await post_files(file)

    # アップロードしたファイルの情報をデータベースに保存
    db_file = await post_filename_to_db(db, file)

    return db_file