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
from utils.sidebar import show_sidebar

# 環境変数を読み込む
load_dotenv()

BACKEND_HOST = os.getenv("BACKEND_HOST")

IMG_PATH = "imgs"


def upload_files() -> None:
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
    if st.button("Submit"):
        try:
            response = requests.get(BACKEND_HOST)
            message = response.json()
            st.text(message["message"])
        except Exception as e:
            st.text("An error occurred.")
            st.text(e)


def main() -> None:
    submit()
    upload_files()

    img = Image.open("AIサポート学習帳.jpg")
    st.image(img, use_column_width=True)


if __name__ == "__main__":
    show_sidebar()
    main()
