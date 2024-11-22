import logging
import os
from typing import List

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

# Firebase認証情報と許可されたドメインを環境変数から取得
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")
ALLOWED_DOMAINS = os.getenv("ALLOWED_DOMAINS", "").split(",")

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


def is_allowed_domain(email: str, allowed_domains: List[str]) -> bool:
    """
    メールアドレスのドメインが許可リストに含まれているか確認する

    :param email: チェックするメールアドレス
    :param allowed_domains: 許可されたドメインのリスト
    :return: ドメインが許可されている場合はTrue
    """
    if not email or "@" not in email:
        return False

    domain = email.split("@")[1].lower()
    return any(domain == allowed_domain.lower().strip() for allowed_domain in allowed_domains)


def authenticate_request(
    request: Request, credentials: HTTPAuthorizationCredentials = dependency
) -> None:
    """
    ユーザー認証を行い、UIDとEmailをリクエストのstateに保存する関数

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
        request.state.email = "test@example.com"
        return None

    token = credentials.credentials
    try:
        # Firebaseトークンを検証
        decoded_token = auth.verify_id_token(token)

        # UIDとEmailを取得
        uid = decoded_token.get("uid")
        email = decoded_token.get("email")

        if not uid:
            logger.error("Invalid token: UID not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: UID not found",
                headers={"WWW-Authenticate": 'Bearer realm="auth_required"'},
            )

        if not email:
            logger.error("Invalid token: Email not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: Email not found",
                headers={"WWW-Authenticate": 'Bearer realm="auth_required"'},
            )

        # ドメインの検証
        if not is_allowed_domain(email, ALLOWED_DOMAINS):
            error_msg = f"Email domain not allowed: {email}"
            logger.error(error_msg)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_msg,
                headers={"WWW-Authenticate": 'Bearer error="forbidden"'},
            )

        # UIDとEmailをリクエストのstateに保存
        request.state.uid = uid
        request.state.email = email
        logger.debug(f"Authenticated user with UID: {uid} and Email: {email}")
        return None

    except HTTPException:
        raise
    except auth.InvalidIdTokenError as err:
        # Firebase認証エラーは401として扱う
        logger.error(f"Invalid token error: {err}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {err}",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
        ) from err
    except Exception as err:
        # その他の予期しないエラーは401として扱う
        logger.error(f"Unexpected authentication error: {err}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {err}",
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


def get_email(request: Request) -> str:
    """
    リクエストのstateからEmailを取得する依存関数

    :param request: FastAPIのRequestオブジェクト
    :return: ユーザーのEmail
    :raises HTTPException: Emailが存在しない場合
    """
    email = getattr(request.state, "email", None)
    if email is None:
        logger.error("Email not found in request state")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not found in request state.",
            headers={"WWW-Authenticate": 'Bearer realm="auth_required"'},
        )
    return email
