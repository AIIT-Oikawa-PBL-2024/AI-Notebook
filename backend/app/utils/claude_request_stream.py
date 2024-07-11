import asyncio
import base64
import io
import logging
import os
from typing import AsyncGenerator

import fitz
from anthropic import AnthropicVertex
from dotenv import load_dotenv
from google.api_core.exceptions import (
    GoogleAPIError,
    InternalServerError,
)
from google.cloud import storage

# 環境変数を読み込む
load_dotenv()

# プロジェクトIDとリージョンを環境変数から取得
PROJECT_ID = str(os.getenv("PROJECT_ID"))
REGION = "europe-west1"  # リージョンは固定
MODEL_NAME = "claude-3-5-sonnet@20240620"  # Claudeモデル名は固定
BUCKET_NAME: str = str(os.getenv("BUCKET_NAME"))


# ロギングの設定
logging.basicConfig(level=logging.INFO)


# Google Cloud Storageでファイルが存在するかチェック
async def check_file_exists(bucket_name: str, file_name: str) -> bool:
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    return blob.exists()


# GCSのファイル読み込み
async def read_file(bucket_name: str, file_name: str) -> str:
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    async with blob.open("rb") as f:
        file_content = await f.read()
    # base64エンコーディング
    base64_encoded = base64.b64encode(file_content).decode("utf-8")
    return base64_encoded


# pdfからテキスト抽出
async def extract_text_from_pdf(bucket_name: str, file_name: str) -> str:
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    # blobの内容をメモリにダウンロード
    pdf_content = await asyncio.to_thread(blob.download_as_bytes)
    # BytesIOオブジェクトを作成
    pdf_file = io.BytesIO(pdf_content)
    # PDFファイルを開く
    doc = await asyncio.to_thread(fitz.open, stream=pdf_file, filetype="pdf")
    extracted_text = ""
    for i, page in enumerate(doc):
        page_text = await asyncio.to_thread(page.get_text)
        extracted_text += f"\n# {i+1}ページ\n{page_text}"
    return extracted_text


# 複数のimageファイルを入力してコンテンツを生成
async def generate_content_stream(
    files: list[str],
    model_name: str = MODEL_NAME,
    bucket_name: str = BUCKET_NAME,
) -> AsyncGenerator[str, None]:
    image_files: list[dict] = []
    prompt = """
        - #role: あなたは、わかりやすく丁寧に教えることで評判の大学の「AI教授」です。
        - #input_files: 複数のファイルは、ソフトウェア工学の解説スライドです。
        - #instruction: 複数のpdf, imageファイルを読み解いて、練習問題を作って下さい。
        - #style: "4択の選択問題"を5問 + "穴埋め問題"を5問、合計10問出題してください。
        - #condition1: 重要なキーワードを覚えられるような問題を作成してください。
        - #condition2: 200文字程度の"記述式問題"を3問出題して下さい。
        - #condition3: "表形式"は禁止します。"箇条書き"を使用してください。
        - #condition4: 最後に一括して"正解"と"解説"を箇条書き形式で表示してください。
        - #condition5: 記述式問題の正解は省略せず、"解答例"を表示してください。
        - #format: タイトルを付けて、4000文字程度のMarkdownで出力してください。
    """

    try:
        # モデルのインスタンスを作成
        client = AnthropicVertex(region=REGION, project_id=PROJECT_ID)

        for file_name in files:
            # ファイルがGCSに存在するかチェック
            if await check_file_exists(bucket_name, file_name):
                if file_name.lower().endswith(
                    (".png", ".jpg", ".jpeg", ".gif", "webp")
                ):
                    image_file = await read_file(bucket_name, file_name)
                    file_extension = file_name.split(".")[-1].lower()
                    image_files.append(
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": f"image/{file_extension}",
                                "data": image_file,
                            },
                        }
                    )
                if file_name.lower().endswith(".pdf"):
                    extracted_text = await extract_text_from_pdf(bucket_name, file_name)

        # 動的にcontentを作成
        content: list = []
        if image_files:
            for i, image in enumerate(image_files, 1):
                content.extend([{"type": "text", "text": f"Image {i}:"}, image])

        # pdfファイルがある場合は、それも追加
        if extracted_text:
            content.append({"type": "text", "text": extracted_text})

        # 最後にプロンプトを追加
        content.append({"type": "text", "text": prompt})

        with client.messages.stream(
            max_tokens=4096,
            temperature=0.1,
            messages=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
            model=model_name,
        ) as stream:
            for text in stream.text_stream:
                yield text

    except AttributeError as e:
        logging.error(f"Model attribute error: {e}")
        raise
    except TypeError as e:
        logging.error(f"Type error in model generation: {e}")
        raise
    except InternalServerError as e:
        logging.error(f"Internal server error: {e}")
        raise
    except GoogleAPIError as e:
        logging.error(f"Google API error: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error during content generation: {e}")
        raise


# テスト用のコード
async def main() -> None:
    response: AsyncGenerator = generate_content_stream(
        # ["kougi_sample.png", "kougi_sample2.png"],
        ["1_ソフトウェア工学の誕生.pdf"]
    )

    async for content in response:
        print(content, end="")


if __name__ == "__main__":
    asyncio.run(main())
