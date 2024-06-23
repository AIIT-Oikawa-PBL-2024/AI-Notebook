import os
from typing import Any  # Add this line

import httpx
import streamlit as st

# サイドバーメニューを表示する
with st.sidebar:
    st.page_link("main.py", label="トップページ")
    st.page_link("pages/upload_files.py", label=
                 "ノート・AIサポート学習帳")
    st.page_link("pages/upload_files.py", label=
                 "AIサポートテスト")
    st.page_link("pages/upload_files.py", label=
                 "ファイル選択")

# Constants
ALLOWED_EXTENSIONS = ["pdf", "jpg", "jpeg", "png"]
#MAX_FILE_SIZE = 200 * 1024 * 1024  # 200 MB in bytes


def is_valid_file(file: Any) -> bool:
    # Check file extension
    file_ext = os.path.splitext(file.name)[1][1:].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        st.error(
            f" {file.name}をアップロードできませんでした。PDF、JPG、JPEG、"
            "またはPNGファイルをアップロードしてください"
        )
        return False

    # Check file size
    #if file.size > MAX_FILE_SIZE:
    #    st.error(
    #        f"{file.name}をアップロードできませんでした。200 MB以下のファイルを"
    #        "アップロードしてください。"
    #    )
    #    return False

    return True

def main() -> None:
    st.title("ファイルアップロード")
    # 学習帳名の入力
    #note_name = st.text_input("学習帳名を入力してください")
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
