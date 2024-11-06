import os
from typing import Callable, Dict

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import exercises, files, notes, outputs_stream
from app.utils.user_auth import authenticate_request, get_uid

# FastAPIのインスタンスを作成
app = FastAPI()


# テスト環境での認証バイパス用の関数
def get_auth_dependency() -> Callable:
    if os.getenv("TESTING") == "True":
        return lambda: None
    return authenticate_request


# ルーターを登録（認証を注入）
app.include_router(files.router, dependencies=[Depends(get_auth_dependency())])
app.include_router(outputs_stream.router, dependencies=[Depends(get_auth_dependency())])
app.include_router(notes.router, dependencies=[Depends(get_auth_dependency())])
app.include_router(
    exercises.router, dependencies=[Depends(get_auth_dependency())]
)

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


# 認証が必要なエンドポイントの例（ルートレベルでの認証確認）
@app.get("/protected")
async def protected_route(uid: str = Depends(get_uid)) -> Dict[str, str]:
    return {"message": f"認証されたユーザー: {uid}"}
