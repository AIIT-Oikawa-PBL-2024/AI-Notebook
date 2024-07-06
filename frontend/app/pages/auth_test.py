# Cloud Runのbackendサービスに認証付きでリクエストを送信するサンプルコード
import asyncio
import os

import httpx
import streamlit as st
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.id_token import fetch_id_token

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数から取得
BACKEND_HOST = os.getenv("BACKEND_HOST")

# Cloud RunのサービスURL
audience = str(BACKEND_HOST)
endpoint = f"{BACKEND_HOST}/"


# Cloud Runのbackendサービスにリクエストを送信する関数
async def make_request(audience: str, endpoint: str) -> dict:
    auth_req = Request()
    id_token = fetch_id_token(auth_req, audience)
    headers = {"Authorization": f"Bearer {id_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(endpoint, headers=headers)
        response.raise_for_status()  # エラーチェックを追加
        return response.json()


st.title("Cloud Run Request Example")

if st.button("Send Request"):
    try:
        response = asyncio.run(make_request(audience=audience, endpoint=endpoint))
        st.write(response)
    except httpx.HTTPStatusError as e:
        st.error(f"HTTPエラーが発生しました: {e.response.status_code}")
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
