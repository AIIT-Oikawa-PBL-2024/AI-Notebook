import os
from typing import Any

import httpx
import streamlit as st

with st.sidebar:
    st.page_link("main.py", label="トップページ")
    st.page_link("pages/study_ai_note.py", label="ノート・AIサポート学習帳")
    st.page_link("pages/select_files.py", label="ファイル選択")

ALLOWED_EXTENSIONS = ["pdf", "jpg", "jpeg", "png"]


def is_valid_file(file: Any) -> bool:
    """
    Check if the file has a valid extension.

    Args:
        file (Any): The file to be checked.

    Returns:
        bool: True if the file has a valid extension, False otherwise.
    """
    file_ext = os.path.splitext(file.name)[1][1:].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        st.error(
            f" {file.name}をアップロードできませんでした。PDF、JPG、JPEG、"
            "またはPNGファイルをアップロードしてください"
        )
        return False

    return True


def main() -> None:
    """
    Main function for file upload.

    This function displays a file uploader and handles the file upload process.
    """
    st.title("ファイルアップロード")
    uploaded_files = st.file_uploader(
        "", accept_multiple_files=True, label_visibility="collapsed"
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
                    f" {file.name}は正常にアップロードされました。 (Size: "
                    + f"{file.size / 1024 / 1024:.2f} MB)"
                )

        if valid_files:
            if st.button("アップロード"):
                try:
                    with httpx.Client() as client:
                        files = {f.name: f.getvalue() for f in valid_files}
                        response = client.post(
                            "http://127.0.0.1:8000/files/upload", files=files
                        )

                        if response.status_code == 200:
                            st.success("ファイルは正常に登録されました。")
                        else:
                            st.error(
                                "ファイルは登録できませんでした。 Status code: "
                                "{response.status_code}"
                            )
                except httpx.RequestError as e:
                    st.error(f"リクエストでエラーが発生しました：{e}")
            elif st.button("学習帳出力"):
                try:
                    with httpx.Client() as client:
                        files = {f.name: f.getvalue() for f in valid_files}
                        response = client.post(
                            "http://127.0.0.1:8000/files/upload", files=files
                        )

                        if response.status_code == 200:
                            st.success("ファイルは正常に登録されました。")
                        else:
                            st.error(
                                f"ファイルは登録できませんでした。 Status code: "
                                f"{response.status_code}"
                            )
                except httpx.RequestError as e:
                    st.error(f"リクエストでエラーが発生しました：{e}")


if __name__ == "__main__":
    main()
