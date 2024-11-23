import os
import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from unittest.mock import MagicMock, patch
from firebase_admin import auth
from app.utils.user_auth import (
    authenticate_request,
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


def test_is_allowed_domain() -> None:
    """ドメイン検証機能のテスト"""
    # 有効なケース
    assert is_allowed_domain("user@example.com", TEST_ALLOWED_DOMAINS) is True
    assert is_allowed_domain("user@allowed-domain.com", TEST_ALLOWED_DOMAINS) is True

    # 無効なケース
    assert is_allowed_domain("user@invalid-domain.com", TEST_ALLOWED_DOMAINS) is False
    assert is_allowed_domain("invalid-email", TEST_ALLOWED_DOMAINS) is False
    assert is_allowed_domain("", TEST_ALLOWED_DOMAINS) is False


def test_authenticate_request_test_environment(
    mock_request: Request, mock_credentials: HTTPAuthorizationCredentials
) -> None:
    """テスト環境での認証処理のテスト"""
    # テスト環境フラグを設定
    os.environ["TESTING"] = "True"

    try:
        authenticate_request(mock_request, mock_credentials)
        assert mock_request.state.uid == "test_user"
        assert mock_request.state.email == "test@example.com"
    finally:
        # テスト環境フラグをリセット
        os.environ["TESTING"] = "False"


def test_authenticate_request_success(
    mock_request: Request, mock_credentials: HTTPAuthorizationCredentials
) -> None:
    """正常な認証フローのテスト"""
    # テスト環境フラグを無効化
    os.environ["TESTING"] = "False"

    # Firebase認証のモック
    mock_decoded_token = {"uid": TEST_UID, "email": TEST_EMAIL}

    with patch("app.utils.user_auth.auth.verify_id_token") as mock_verify:
        mock_verify.return_value = mock_decoded_token
        with patch("app.utils.user_auth.ALLOWED_DOMAINS", TEST_ALLOWED_DOMAINS):
            authenticate_request(mock_request, mock_credentials)

            assert mock_request.state.uid == TEST_UID
            assert mock_request.state.email == TEST_EMAIL
            mock_verify.assert_called_once_with(TEST_TOKEN)


def test_authenticate_request_invalid_token(
    mock_request: Request, mock_credentials: HTTPAuthorizationCredentials
) -> None:
    """無効なトークンの場合のテスト"""
    # テスト環境フラグを無効化
    os.environ["TESTING"] = "False"

    with patch("app.utils.user_auth.auth.verify_id_token") as mock_verify:
        mock_verify.side_effect = auth.InvalidIdTokenError("Invalid token")

        with pytest.raises(HTTPException) as exc_info:
            authenticate_request(mock_request, mock_credentials)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid authentication credentials" in str(exc_info.value.detail)


def test_authenticate_request_forbidden_domain(
    mock_request: Request, mock_credentials: HTTPAuthorizationCredentials
) -> None:
    """許可されていないドメインの場合のテスト"""
    # テスト環境フラグを無効化
    os.environ["TESTING"] = "False"

    forbidden_email = "user@forbidden-domain.com"
    mock_decoded_token = {"uid": TEST_UID, "email": forbidden_email}

    with patch("app.utils.user_auth.auth.verify_id_token") as mock_verify:
        mock_verify.return_value = mock_decoded_token
        with patch("app.utils.user_auth.ALLOWED_DOMAINS", new=TEST_ALLOWED_DOMAINS):
            with pytest.raises(HTTPException) as exc_info:
                authenticate_request(mock_request, mock_credentials)

            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
            assert "Email domain not allowed" in str(exc_info.value.detail)
            mock_verify.assert_called_once_with(TEST_TOKEN)


def test_get_uid_success(mock_request: Request) -> None:
    """UIDの取得成功テスト"""
    mock_request.state.uid = TEST_UID
    assert get_uid(mock_request) == TEST_UID


def test_get_uid_not_found(mock_request: Request) -> None:
    """UIDが見つからない場合のテスト"""
    mock_request.state.uid = None
    with pytest.raises(HTTPException) as exc_info:
        get_uid(mock_request)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "UID not found" in str(exc_info.value.detail)


def test_get_email_success(mock_request: Request) -> None:
    """メールアドレスの取得成功テスト"""
    mock_request.state.email = TEST_EMAIL
    assert get_email(mock_request) == TEST_EMAIL


def test_get_email_not_found(mock_request: Request) -> None:
    """メールアドレスが見つからない場合のテスト"""
    mock_request.state.email = None
    with pytest.raises(HTTPException) as exc_info:
        get_email(mock_request)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Email not found" in str(exc_info.value.detail)
