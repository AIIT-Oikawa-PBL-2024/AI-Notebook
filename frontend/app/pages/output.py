import asyncio
import io
from typing import AsyncIterator, List

import httpx
import streamlit as st  # type: ignore


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


if __name__ == "__main__":
    show_output_markdown()
