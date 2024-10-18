import logging
import os

import firebase_admin
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth, credentials
from starlette.requests import Request

# ロギングの設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# .envファイルから環境変数を読み込む
load_dotenv()

# Firebase認証情報を環境変数から取得
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")

# HTTPBearer認証スキームを初期化
http_bearer = HTTPBearer(auto_error=True)
dependency = Depends(http_bearer)

# テスト環境でない場合のみFirebaseを初期化
if os.getenv("TESTING") != "True":
    if FIREBASE_CREDENTIALS is None:
        raise ValueError("FIREBASE_CREDENTIALS environment variable not set")

    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred)
    logger.info("Firebase initialized")
else:
    logger.info("Skipping Firebase initialization in test environment")


def authenticate_request(
    request: Request, credentials: HTTPAuthorizationCredentials = dependency
) -> None:
    """
    ユーザー認証を行い、UIDをリクエストのstateに保存する関数

    :param request: FastAPIのRequestオブジェクト
    :param credentials: HTTPAuthorizationCredentials（Bearerトークン）
    :return: なし
    :raises HTTPException: 認証に失敗した場合
    """
    logger.debug(f"TESTING env var: {os.getenv('TESTING')}")
    logger.debug(f"Authorization header: {credentials.credentials}")

    # テスト環境の場合は認証をスキップ
    if os.getenv("TESTING") == "True":
        logger.debug("Bypassing authentication for test environment")
        request.state.uid = "test_user"
        return

    token = credentials.credentials
    try:
        # Firebaseトークンを検証
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token.get("uid")
        if not uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: UID not found",
                headers={"WWW-Authenticate": 'Bearer realm="auth_required"'},
            )
        # UIDをリクエストのstateに保存
        request.state.uid = uid
        logger.debug(f"Authenticated user with UID: {uid}")
    except Exception as err:
        logger.error(f"Authentication error: {err}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials. {err}",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
        ) from err


def get_uid(request: Request) -> str:
    """
    リクエストのstateからUIDを取得する依存関数

    :param request: FastAPIのRequestオブジェクト
    :return: ユーザーのUID
    :raises HTTPException: UIDが存在しない場合
    """
    uid = getattr(request.state, "uid", None)
    if uid is None:
        logger.error("UID not found in request state")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UID not found in request state.",
            headers={"WWW-Authenticate": 'Bearer realm="auth_required"'},
        )
    return uid
