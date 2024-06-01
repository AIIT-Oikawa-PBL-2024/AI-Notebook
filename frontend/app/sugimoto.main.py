import asyncio
import os
from typing import Any, Dict, List

import httpx
import streamlit as st
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

BACKEND_HOST = os.getenv("BACKEND_HOST")

st.title("Frontend App")
st.markdown("This is a frontend application that communicates with a backend service.")


def sidebar() -> None:
    with st.sidebar:
        st.page_link("main.py", label="ホーム", icon="🏠")
        st.page_link("pages/01_page1.py", label="マルチページ1", icon="1️⃣")
        st.page_link("pages/02_page2.py", label="マルチページ2", icon="2️⃣")


async def upload_files_and_get_response(files: List) -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient() as client:
            # 複数のファイルをmultipart/form-dataとして送信
            file_data = {
                f"file{i}": (file.name, file, file.type) for i, file in enumerate(files)
            }
            response = await client.post(
                str(BACKEND_HOST), files=file_data
            )  # Replace BACKEND_HOST with str(BACKEND_HOST)
            return response.json()
    except Exception as e:
        st.text("An error occurred.")
        st.text(str(e))
        return {"error": str(e)}


def main() -> None:
    uploaded_files = st.file_uploader(
        "ファイルをアップロードしてください",
        accept_multiple_files=True,
        type=["png", "jpg", "jpeg", "pdf"],
    )

    if st.button("Submit"):
        if uploaded_files is not None:
            result = asyncio.run(upload_files_and_get_response(list(uploaded_files)))
            st.text(result)


if __name__ == "__main__":
    sidebar()
    main()