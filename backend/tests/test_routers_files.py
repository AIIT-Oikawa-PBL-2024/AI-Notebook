import pytest
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
import unicodedata
from unittest.mock import Mock

# .envファイルから環境変数を読み込む
load_dotenv()


# ファイルアップロードのテスト
@pytest.mark.asyncio
async def test_upload_files(session: AsyncSession, mock_auth: Mock) -> None:
    file_content = b"test file content"
    files = [
        ("files", ("test_file.pdf", file_content, "application/pdf")),
    ]
    headers = {"Authorization": "Bearer fake_token"}
    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        response = await client.post("/files/upload", files=files, headers=headers)
        print(response.text)  # デバッグ用出力
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["success_files"]) == 1


# ファイル一覧取得のテスト
@pytest.mark.asyncio
async def test_get_files(session: AsyncSession, mock_auth: Mock) -> None:
    headers = {"Authorization": "Bearer fake_token"}
    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        file_content = b"test file content"
        files = [
            ("files", ("test_file.pdf", file_content, "application/pdf")),
        ]
        await client.post(f"/files/upload", files=files, headers=headers)

        response = await client.get("/files/", headers=headers)
        print(response.text)  # デバッグ用出力
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0


# ファイルIDによるファイル取得のテスト
@pytest.mark.asyncio
async def test_get_file_by_id(session: AsyncSession, mock_auth: Mock) -> None:
    headers = {"Authorization": "Bearer fake_token"}
    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        file_content = b"test file content"
        files = [
            ("files", ("test_file.pdf", file_content, "application/pdf")),
        ]
        await client.post(f"/files/upload", files=files, headers=headers)

        response = await client.get("/files/1", headers=headers)
        print(response.text)  # デバッグ用出力
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["file_name"] == "test_file.pdf"


# ファイル名のリストとユーザーIDによるファイルの削除のテスト
@pytest.mark.asyncio
async def test_delete_files(session: AsyncSession, mock_auth: Mock) -> None:
    headers = {"Authorization": "Bearer fake_token"}
    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        file_content = b"test file content"
        files = [
            ("files", ("test_file1.pdf", file_content, "application/pdf")),
            ("files", ("test_file2.pdf", file_content, "application/pdf")),
        ]
        await client.post(f"/files/upload", files=files, headers=headers)

        delete_files = ["test_file1.pdf", "test_file2.pdf"]
        response = await client.request(
            method="DELETE",
            url="/files/delete_files",
            json=delete_files,
            headers=headers,
        )
        print(response.text)  # デバッグ用出力
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["success_files"]) == 2
        # 各成功ファイルの内容を確認
        for file_info in data["success_files"]:
            assert "message" in file_info
            assert "filename" in file_info
            assert file_info["message"].endswith("が削除されました")


# 存在しないファイルIDによるファイル取得のテスト
@pytest.mark.asyncio
async def test_get_file_by_id_not_found(session: AsyncSession, mock_auth: Mock) -> None:
    headers = {"Authorization": "Bearer fake_token"}
    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        response = await client.get("/files/9999", headers=headers)
        print(response.text)  # デバッグ用出力
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "ファイルが見つかりません"


# 濁点を含むファイル名のNFC正規化テスト
@pytest.mark.asyncio
async def test_upload_file_with_dakuten(session: AsyncSession, mock_auth: Mock) -> None:
    headers = {"Authorization": "Bearer fake_token"}

    # NFD形式（濁点が分離された形式）の日本語ファイル名
    nfd_filename = "テスト" + "\u3099" + "ファイル.pdf"  # "テストゞファイル.pdf"のNFD形式
    nfc_filename = unicodedata.normalize("NFC", nfd_filename)

    file_content = b"test file content with dakuten"
    files = [
        ("files", (nfd_filename, file_content, "application/pdf")),
    ]

    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        response = await client.post("/files/upload", files=files, headers=headers)
        print(response.text)  # デバッグ用出力
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["success_files"]) == 1

        # アップロードされたファイルの情報を取得
        file_response = await client.get("/files/", headers=headers)
        assert file_response.status_code == 200
        file_data = file_response.json()

        # 最後にアップロードされたファイルのファイル名を確認
        uploaded_filename = file_data[-1]["file_name"]

        # ファイル名がNFC形式になっていることを確認
        assert uploaded_filename == nfc_filename
        assert uploaded_filename != nfd_filename
        assert unicodedata.is_normalized("NFC", uploaded_filename)


# 署名付きURL取得のテスト
@pytest.mark.asyncio
async def test_generate_upload_signed_url(session: AsyncSession) -> None:
    headers = {"Authorization": "Bearer fake_token"}
    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        testfiles = ["test_file1.pdf", "test_file2.pdf"]
        response = await client.post(
            f"/files/generate_upload_signed_url",
            headers=headers,
            json=testfiles,
        )
        print(response.text)  # デバッグ用出力
        assert response.status_code == 200
        data = response.json()
        assert data["test_user/test_file1.pdf"] is not None
        assert data["test_user/test_file2.pdf"] is not None


# ファイル登録のテスト
@pytest.mark.asyncio
async def test_register_files(session: AsyncSession) -> None:
    """
    ファイル登録のエンドポイントをテストする関数

    :param session: テスト用のデータベースセッション
    :type session: AsyncSession
    :return: None
    :raises AssertionError: テストが失敗した場合
    """
    headers = {"Authorization": "Bearer fake_token"}

    file_content = b"test file content"
    files = [
        ("files", ("test_file.pdf", file_content, "application/pdf")),
    ]
    async with AsyncClient(
        transport=ASGITransport(app),  # type: ignore
        base_url="http://test",
    ) as client:
        response = await client.post(f"/files/register_files", files=files, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data is True
