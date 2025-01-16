import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from unittest.mock import MagicMock
from firebase_admin import auth
from app.utils.user_auth import (
    is_allowed_domain,
    get_uid,
    get_email,
)
from starlette.requests import Request

# テスト用の固定値
TEST_TOKEN = "test_token"
TEST_UID = "test_uid"
TEST_EMAIL = "user@example.com"
TEST_ALLOWED_DOMAINS = ["example.com", "allowed-domain.com"]


@pytest.fixture
def mock_request() -> Request:
    """リクエストオブジェクトのモック"""
    request = MagicMock()
    request.state = MagicMock()
    return request


@pytest.fixture
def mock_credentials() -> HTTPAuthorizationCredentials:
    """認証情報のモック"""
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=TEST_TOKEN)


@pytest.mark.asyncio
async def test_is_allowed_domain() -> None:
    """ドメイン検証機能のテスト"""
    # 有効なケース
    assert await is_allowed_domain("user@example.com", TEST_ALLOWED_DOMAINS) is True
    assert await is_allowed_domain("user@allowed-domain.com", TEST_ALLOWED_DOMAINS) is True

    # 無効なケース
    assert await is_allowed_domain("user@invalid-domain.com", TEST_ALLOWED_DOMAINS) is False
    assert await is_allowed_domain("invalid-email", TEST_ALLOWED_DOMAINS) is False
    assert await is_allowed_domain("", TEST_ALLOWED_DOMAINS) is False


# 以下のテスト関数は既に非同期対応済みのため変更不要
@pytest.mark.asyncio
async def test_authenticate_request_test_environment(
    mock_request: Request, mock_credentials: HTTPAuthorizationCredentials
) -> None:
    """テスト環境での認証処理のテスト"""
    # ...（既存のコード）


@pytest.mark.asyncio
async def test_authenticate_request_success(
    mock_request: Request, mock_credentials: HTTPAuthorizationCredentials
) -> None:
    """正常な認証フローのテスト"""
    # ...（既存のコード）


@pytest.mark.asyncio
async def test_authenticate_request_invalid_token(
    mock_request: Request, mock_credentials: HTTPAuthorizationCredentials
) -> None:
    """無効なトークンの場合のテスト"""
    # ...（既存のコード）


@pytest.mark.asyncio
async def test_authenticate_request_forbidden_domain(
    mock_request: Request, mock_credentials: HTTPAuthorizationCredentials
) -> None:
    """許可されていないドメインの場合のテスト"""
    # ...（既存のコード）


@pytest.mark.asyncio
async def test_get_uid_success(mock_request: Request) -> None:
    """UIDの取得成功テスト"""
    mock_request.state.uid = TEST_UID
    result = await get_uid(mock_request)
    assert result == TEST_UID


@pytest.mark.asyncio
async def test_get_uid_not_found(mock_request: Request) -> None:
    """UIDが見つからない場合のテスト"""
    mock_request.state.uid = None
    with pytest.raises(HTTPException) as exc_info:
        await get_uid(mock_request)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "UID not found" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_email_success(mock_request: Request) -> None:
    """メールアドレスの取得成功テスト"""
    mock_request.state.email = TEST_EMAIL
    result = await get_email(mock_request)
    assert result == TEST_EMAIL


@pytest.mark.asyncio
async def test_get_email_not_found(mock_request: Request) -> None:
    """メールアドレスが見つからない場合のテスト"""
    mock_request.state.email = None
    with pytest.raises(HTTPException) as exc_info:
        await get_email(mock_request)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Email not found" in str(exc_info.value.detail)
