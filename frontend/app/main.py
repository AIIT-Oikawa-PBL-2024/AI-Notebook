## Issue No.2
## Title Input:画像入力インターフェース機能
##タスク1,3,4
##https://github.com/orgs/AIIT-Oikawa-PBL-2024/projects/9/views/1?sortedBy%5Bdirection%5D=asc&sortedBy%5BcolumnId%5D=108570462

## 概要
##AIサポート学習帳の画像アップロード画面
##ファイルタイプを'png', 'pdf', 'jpeg', 'jpg'に制限する
##ファイルサイズは‘.streamlit/config.toml’で変更（デフォルト200MB）

import os

import requests  # type: ignore
import streamlit as st
from dotenv import load_dotenv
from PIL import Image

# 環境変数を読み込む
load_dotenv()

BACKEND_HOST = os.getenv("BACKEND_HOST")

IMG_PATH = "imgs"


def upload_files() -> None:
    """
    Uploads image files to the AI Support Learning Book.

    This function allows the user to upload image files (png, pdf, jpeg, jpg) to the AI Support Learning Book.
    The uploaded files are saved in the 'imgs' directory.

    Returns:
        None
    """
    st.markdown("# AIサポート学習帳　ファイルアップロード")
    files = st.file_uploader(
        "講義テキストの画像をアップロードしてください.",
        accept_multiple_files=True,
        type=["png", "pdf", "jpeg", "jpg"],
    )

    if files:
        for file in files:
            st.markdown(f"{file.name} をアップロードしました.")
            with open(os.path.join(IMG_PATH, file.name), "wb") as f:
                f.write(file.getbuffer())


def submit() -> None:
    """
    Submits the uploaded files to the backend server.

    This function sends a request to the backend server with the uploaded files.
    If the submission is successful, the server's response message is displayed.

    Returns:
        None
    """
    if st.button("Submit"):
        try:
            response = requests.get(BACKEND_HOST)
            message = response.json()
            st.text(message["message"])
        except Exception as e:
            st.text("An error occurred.")
            st.text(e)


def main() -> None:
    """
    Main function of the AI Support Learning Book application.

    This function is the entry point of the application.
    It calls the 'submit' and 'upload_files' functions and displays the uploaded image.

    Returns:
        None
    """
    submit()
    upload_files()

    img = Image.open("AIサポート学習帳.jpg")
    st.image(img, use_column_width=True)


if __name__ == "__main__":
    main()
