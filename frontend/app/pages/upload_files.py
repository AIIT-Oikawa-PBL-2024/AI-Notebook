import os
from typing import Any  # Add this line

import httpx
import streamlit as st

# Read links from an external file
with open("links.txt", "r") as f:
    links = f.readlines()

# Display links in the sidebar
with st.sidebar:
    for link in links:
        link_parts = link.strip().split(",")
        st.page_link(link_parts[0], label=link_parts[1], icon=link_parts[2])

# Constants
ALLOWED_EXTENSIONS = ["pdf", "jpg", "jpeg", "png"]
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200 MB in bytes


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
    if file.size > MAX_FILE_SIZE:
        st.error(
            f"{file.name}をアップロードできませんでした。200 MB以下のファイルを"
            "アップロードしてください。"
        )
        valid_files = []  # Define valid_files as an empty list before using it

        if valid_files:
            if st.button("登録"):
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
                    st.error(f" {e}リクエストでエラーが発生しました。")
        else:
            st.warning(
                "ファイルが登録されませんでした。"
                "有効なファイルをアップロードしてください。"
            )
            st.warning(
                "ファイルが登録されませんでした。"
                "有効なファイルをアップロードしてください。"
            )


def main():
    # Your code here
    pass


if __name__ == "__main__":
    main()
