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
REGION = "us-east5"  # リージョンは固定
MODEL_NAME = "claude-3-5-sonnet@20240620"  # Claudeモデル名は固定
BUCKET_NAME: str = str(os.getenv("BUCKET_NAME"))


# ロギングの設定
logging.basicConfig(level=logging.INFO)


# Google Cloud Storageでファイルが存在するかチェック
async def check_file_exists(bucket_name: str, file_name: str) -> bool:
    """
    Google Cloud Storageで指定されたバケット内のファイルが存在するかどうかを確認

    :param bucket_name: バケット名
    :param file_name: ファイル名
    :return: ファイルの存在を示す真偽値
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    return blob.exists()


# GCSのファイル読み込み
async def read_file(bucket_name: str, file_name: str) -> str:
    """
    Google Cloud Storageからファイルを読み込み、base64エンコードされた文字列として返す

    :param bucket_name: バケット名
    :param file_name: ファイル名
    :return: base64エンコードされたファイル内容
    """
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
    """
    指定されたPDFファイルからテキストを抽出して返す

    :param bucket_name: バケット名
    :param file_name: PDFファイル名
    :return: 抽出されたテキスト
    """
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


# 複数のpdf, imageファイルを入力してコンテンツを生成
async def generate_content_stream(
    files: list[str],
    model_name: str = MODEL_NAME,
    bucket_name: str = BUCKET_NAME,
) -> AsyncGenerator[str, None]:
    print("generate_content_stream started")  # デバッグ用

    image_files: list[dict] = []
    prompt = """
        - #role: あなたは、わかりやすく丁寧に教えることで評判の大学の「AI教授」です。
        - #input_files: 複数のファイルは、大学院の講義資料です。
        - #instruction: 複数のpdf, imageファイルを読み解いて、練習問題を作って下さい。
        - #style1: "4択の選択問題"を5問 + "穴埋め問題"を5問、合計10問出題してください。
        - #style2: 200文字程度の"記述式問題"を3問出題して下さい。
        - #style3: 最後に一括して"正解"と"解説"を箇条書き形式で表示してください。
        - #style4: 記述式問題の正解は省略せず、"解答例"を表示してください。
        - #condition1: 重要なキーワードを覚えられるような問題にしてください。
        - #condition2: "表形式"は禁止します。"箇条書き"を使用してください。
        - #format: タイトルを付けて、4000文字程度のMarkdownで出力してください。
    """

    try:
        client = AnthropicVertex(region=REGION, project_id=PROJECT_ID)
        extracted_text = ""  # 初期化
        for file_name in files:
            print(f"Processing file: {file_name}")  # デバッグ用
            if await check_file_exists(bucket_name, file_name):
                print(f"File {file_name} exists in bucket {bucket_name}")  # デバッグ用
                if file_name.lower().endswith(
                    (".png", ".jpg", ".jpeg", ".gif", "webp")
                ):
                    print(f"Reading image file: {file_name}")  # デバッグ用
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
                    print(f"Added image file: {file_name} to image_files")  # デバッグ用
                if file_name.lower().endswith(".pdf"):
                    print(f"Extracting text from PDF: {file_name}")  # デバッグ用
                    extracted_text = await extract_text_from_pdf(bucket_name, file_name)
                    print(f"Extracted text length: {len(extracted_text)}")  # デバッグ用

        print(f"Total image files processed: {len(image_files)}")  # デバッグ用

        content: list = []
        if image_files:
            for i, image in enumerate(image_files, 1):
                content.extend([{"type": "text", "text": f"Image {i}:"}, image])
            print(f"Added {len(image_files)} images to content")  # デバッグ用

        if extracted_text:
            content.append({"type": "text", "text": extracted_text})
            print("Added extracted text to content")  # デバッグ用

        content.append({"type": "text", "text": prompt})
        print("Added prompt to content")  # デバッグ用

        print(f"Starting stream with model: {model_name}")  # デバッグ用
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

        print("generate_content_stream finished")  # デバッグ用

    except AttributeError as e:
        logging.error(f"Model attribute error: {e}")
        print(f"AttributeError: {e}")  # デバッグ用
        raise
    except TypeError as e:
        logging.error(f"Type error in model generation: {e}")
        print(f"TypeError: {e}")  # デバッグ用
        raise
    except InternalServerError as e:
        logging.error(f"Internal server error: {e}")
        print(f"InternalServerError: {e}")  # デバッグ用
        raise
    except GoogleAPIError as e:
        logging.error(f"Google API error: {e}")
        print(f"GoogleAPIError: {e}")  # デッグ用
        raise
    except Exception as e:
        logging.error(f"Unexpected error during content generation: {e}")
        print(f"Unexpected error: {e}")  # デバッグ用
        raise


# テスト用のコード
async def main() -> None:
    """
    メイン関数。generate_content_stream関数をテストするためのコード
    """
    response: AsyncGenerator = generate_content_stream(
        # ["kougi_sample.png", "kougi_sample2.png"],
        ["1_ソフトウェア工学の誕生.pdf"]
    )

    async for content in response:
        print(content, end="")


if __name__ == "__main__":
    asyncio.run(main())
