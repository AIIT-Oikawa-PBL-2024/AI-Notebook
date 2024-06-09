from typing import Optional

import httpx
import streamlit as st  # type: ignore


def get_output_raw_data() -> Optional[str]:
    # TODO: アウトプットデータの仕様確認後進める
    request_url = "https://localhost:8000/outputs/request"
    headers = {"accept": "application/json", "Content-Type": "application/json"}

    try:
        response = httpx.get(request_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except httpx.HTTPStatusError as hs:
        st.write(f"リクエストが失敗しました: {hs}")
    except Exception as e:
        st.write(f"予期せぬエラーが発生しました: {e}")

    return None


def convert_output_to_markdown() -> None:
    # TODO: 同上
    pass


def show_output_markdown(markdown_text: str = "**テストです**") -> None:
    st.markdown(markdown_text)


if __name__ == "__main__":
    show_output_markdown()
