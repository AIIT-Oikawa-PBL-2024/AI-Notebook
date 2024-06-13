import asyncio
from typing import AsyncIterator, List, Optional

import httpx
import streamlit as st  # type: ignore
from streamlit.uploaded_file_manager import UploadedFile


# Geminiからの出力レスポンスはストリームデータで受け取る
async def generate_gemini_processed_markdown_stream(
    filenames: List[str],
) -> AsyncIterator[str]:
    request_url = "http://127.0.0.1:8001/outputs/request"  # Test Mock server
    # request_url = "https://localhost:8000/outputs/request" # Local FastAPI server

    headers = {"accept": "application/json", "Content-Type": "application/json"}

    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST", request_url, headers=headers, json={"filenames": filenames}
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                yield line


async def display_gemini_processed_markdown(filenames: List[str]) -> None:
    markdown_output = ""
    placeholder = st.empty()
    try:
        async for line in generate_gemini_processed_markdown_stream(filenames):
            markdown_output += line + "\n"
            placeholder.markdown(markdown_output)
    # バックエンドの実装次第で他の例外も追加必要かもしれない
    except Exception as e:
        st.write(f"予期せぬエラーが発生しました。エラー： {e}")


def upload_files() -> Optional[List[UploadedFile]]:
    uploaded_files = st.file_uploader(
        "ファイルをアップロードしてください。", type=["pdf"], accept_multiple_files=True
    )

    return uploaded_files


if __name__ == "__main__":
    uploaded_files = upload_files()
    if uploaded_files:
        uploaded_filenames = [file.name for file in uploaded_files]

    if st.button("作成開始"):
        if uploaded_filenames:
            asyncio.run(display_gemini_processed_markdown(uploaded_filenames))
        else:
            st.error("ファイルをアップロードしてください。")
