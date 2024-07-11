import asyncio
import logging
import os
from typing import AsyncGenerator, List

import httpx
import streamlit as st
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

logging.basicConfig(level=logging.INFO)

BACKEND_HOST = os.getenv("BACKEND_HOST")


async def fetch_gemini_stream_data(
    filenames: List[str], BACKEND_DEV_API_URL: str
) -> AsyncGenerator[str, None]:
    CLIENT_TIMEOUT_SEC = 100.0
    headers = {"accept": "text/event-stream"}
    try:
        async with httpx.AsyncClient(timeout=CLIENT_TIMEOUT_SEC) as client:
            async with client.stream(
                "POST", BACKEND_DEV_API_URL, headers=headers, json=filenames
            ) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk.decode("utf-8")
    except httpx.HTTPStatusError as e:
        logging.error(f"エラーが発生しました: {e}")
        st.error(f"エラーが発生しました: {e}")
    except httpx.RemoteProtocolError as e:
        logging.error(f"通信中にエラーが発生しました: {e}")
        return
    except httpx.RequestError as e:
        logging.error(f"リクエストエラーが発生しました: {e}")
        st.error(f"リクエストエラーが発生しました: {e}")
    except httpx.TimeoutException as e:
        logging.error(f"タイムアウトしました: {e}")
        st.error(f"タイムアウトしました: {e}")
    except Exception as e:
        logging.error(f"問題が発生しました: {e}")
        st.error(f"問題が発生しました: {e}")


async def create_pdf_to_markdown_summary(
    filenames: List[str], BACKEND_DEV_API_URL: str
) -> None:
    output = st.empty()

    stream_content = ""
    async for line in fetch_gemini_stream_data(filenames, BACKEND_DEV_API_URL):
        stream_content += line
        output.markdown(stream_content)
    # await fetch_gemini_stream_data(filenames)


if __name__ == "__main__":
    # TODO: 別ページでアップロードされたファイル一覧からファイル名を取得する
    # uploaded_filenames = [file.name for file in uploaded_files]

    temp_uploaded_filenames = ["5_アジャイルⅡ.pdf"]

    if st.button("要約する"):
        asyncio.run(
            create_pdf_to_markdown_summary(
                temp_uploaded_filenames, f"{BACKEND_HOST}/exercises/request_stream"
            )
        )
