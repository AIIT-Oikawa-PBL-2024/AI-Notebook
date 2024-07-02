from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import files, notes, outputs_stream, users

# FastAPIのインスタンスを作成
app = FastAPI()

# ルーターを登錢
app.include_router(users.router)
app.include_router(files.router)
app.include_router(outputs_stream.router)
app.include_router(notes.router)

# CORSの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root() -> dict[str, str]:  # pragma: no cover
    """
    ルートエンドポイントを読み取ります。

    :return: メッセージを含む辞書
    :rtype: dict[str, str]
    """
    return {"message": "Hello World"}
