from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import files, users

# FastAPIのインスタンスを作成
app = FastAPI()

# ルーターを登錢
app.include_router(users.router)
app.include_router(files.router)

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
    return {"message": "Hello World"}
