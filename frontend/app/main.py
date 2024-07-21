import asyncio
import logging
import os
import sys
from typing import Any, Dict

import httpx
import streamlit as st
from PIL import Image

# プロジェクトルートのパスを取得
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# プロジェクトルートをPythonパスに追加
if project_root not in sys.path:
    sys.path.insert(0, project_root)

logging.basicConfig(level=logging.INFO)

BACKEND_HOST = os.getenv("BACKEND_HOST")
BACKEND_DEV_API_URL = f"{BACKEND_HOST}/files/upload"

ALLOWED_EXTENSIONS = ["pdf", "jpg", "jpeg", "png"]
IMG_PATH = "app/statics/PBLフライヤー1Q.jpg"


def is_valid_file(file: Any) -> bool:
    """
    ファイルの拡張子が有効かどうかをチェックします。

    :param file: チェックするファイル。
    :type file: Any
    :returns: ファイルの拡張子が有効な場合はTrue、それ以外の場合はFalse。
    :rtype: bool
    """
    file_ext = os.path.splitext(file.name)[1][1:].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        st.error(
            f" {file.name}をアップロードできませんでした。PDF、JPG、JPEG、"
            "またはPNGファイルをアップロードしてください"
        )
        return False

    return True


async def upload_files_and_get_response(valid_files: list) -> Dict[str, Any]:
    """
    アップロードされたファイルをサーバーに送信し、レスポンスを取得する非同期関数です。

    :param valid_files: アップロードするファイルのリスト
    :type valid_files: list
    :return: レスポンスのJSONデータ
    :rtype: Dict[str, Any]
    """
    CLIENT_TIMEOUT_SEC = 100.0
    try:
        async with httpx.AsyncClient(timeout=CLIENT_TIMEOUT_SEC) as client:
            files = [("files", (file.name, file, file.type)) for file in valid_files]
            headers = {"accept": "application/json"}
            response = await client.post(
                BACKEND_DEV_API_URL, files=files, headers=headers
            )
            return response.json()
    except httpx.RequestError as e:
        st.error(f"リクエストでエラーが発生しました：{e}")
        return {"error": str(e)}


def main() -> None:
    """
    ファイルアップロードのメイン関数です。

    この関数はファイルアップロードの画面を表示し、ファイルのアップロード処理を担当します。
    """
    st.title("ファイルアップロード")
    uploaded_files = st.file_uploader(
        "ファイルをアップロードしてください",
        accept_multiple_files=True,
        type=["png", "jpg", "jpeg", "pdf"],
    )

    if uploaded_files:
        valid_files = []
        file_names = set()

        for file in uploaded_files:
            if file.name in file_names:
                st.error(
                    f" {file.name}ファイルは既にアップロードされています。"
                    "他のファイルをアップロードしてください。"
                )
                continue

            if is_valid_file(file):
                valid_files.append(file)
                file_names.add(file.name)
                st.success(
                    f"アップロードボタンを押して下さい:  {file.name} (Size: "
                    + f"{file.size / 1024 / 1024:.2f} MB)"
                )

        if valid_files:
            if st.button("アップロード"):
                response = asyncio.run(upload_files_and_get_response(valid_files))
                if "error" in response:
                    st.error(
                        f"ファイルのアップロードに失敗しました: {response['error']}"
                    )
                else:
                    if response.get("success"):
                        st.success("ファイルのアップロードが完了しました。")

                        if response["success_files"]:
                            st.write("成功したファイル:")
                            for success_file in response["success_files"]:
                                st.write(
                                    f"- {success_file['filename']}: "
                                    f"{success_file['message']}"
                                )

                        if response["failed_files"]:
                            st.warning("一部のファイルのアップロードに失敗しました:")
                            for failed_file in response["failed_files"]:
                                st.write(
                                    f"- {failed_file['filename']}: "
                                    f"{failed_file['message']}"
                                )
                        else:
                            st.info("すべてのファイルが正常にアップロードされました。")
                    else:
                        st.error("ファイルのアップロードに失敗しました。")
    img = Image.open(IMG_PATH)
    st.image(img)


if __name__ == "__main__":
    from app.utils.sidebar import show_sidebar

    show_sidebar()
    main()
