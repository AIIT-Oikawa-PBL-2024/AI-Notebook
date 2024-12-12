import asyncio
import base64
import io
import logging
import os
import unicodedata

import fitz
from anthropic import AnthropicVertex
from dotenv import load_dotenv
from google.api_core.exceptions import (
    GoogleAPIError,
    InternalServerError,
)
from google.cloud import storage

from app.utils.convert_mp4_to_mp3 import convert_mp4_to_mp3
from app.utils.gemini_extract_text_from_audio import extract_text_from_audio

# 環境変数を読み込む
load_dotenv()

# プロジェクトIDとリージョンを環境変数から取得
PROJECT_ID = str(os.getenv("PROJECT_ID"))
REGION = "us-east5"  # リージョンは固定
MODEL_NAME = "claude-3-5-sonnet@20240620"  # Claudeモデル名は固定
BUCKET_NAME: str = str(os.getenv("BUCKET_NAME"))


# ロギングの設定
logging.basicConfig(level=logging.INFO)

# ツールの設定
tool_name = "print_essay_questions"

description = """
- あなたは、わかりやすく丁寧に教えることで評判の大学の「AI教授」です。
- 入力された大学院の講義テキストの内容に基づいて、
  理解度を深めるための記述式の練習問題を作成してください。
- "記述問題"と"正解"と"解説"のセットを5問作成してください。
- 重要な概念や用語を確認できる問題を作成してください。
- 以下のruleに従って作成してください。

<rule>
- 入力テキストの内容に基づいて、記述問題を5問作成してください。
- 各問題には、問題文、正解、詳しい解説を含めてください。
- 問題は簡易な説明問題から、応用的・発展的な論述を要求する問題へと段階的に難易度を上げてください。
- 全体として、テキストの主要テーマ・概念・定義・理論構造の
  理解や応用力を評価できる内容にしてください。
- 問題のフォーマットは以下の形式に従ってください：
  question_[番号]: 問題文
  answer_[番号]: 回答例
  explanation_[番号]: 解説
</rule>
"""

tool_definition = {
    "name": "print_essay_questions",
    "description": description,
    "input_schema": {
        "type": "object",
        "properties": {
            "questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question_id": {
                            "type": "string",
                            "description": "問題番号 (例: question_1)",
                        },
                        "question_text": {
                            "type": "string",
                            "description": "問題文",
                        },
                        "answer": {
                            "type": "string",
                            "description": "回答例",
                        },
                        "explanation": {
                            "type": "string",
                            "description": "解説文",
                        },
                    },
                    "required": [
                        "question_id",
                        "question_text",
                        "answer",
                        "explanation",
                    ],
                },
                "minItems": 5,
                "maxItems": 5,
            }
        },
        "required": ["questions"],
    },
}


prompt = f"""
{tool_name} ツールのみを利用すること。
"""


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
    # asyncio.to_threadを使用して同期的な操作を非同期に変換
    file_content = await asyncio.to_thread(blob.download_as_bytes)
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


# ファイル拡張子から適切なmedia_typeを返す
def get_media_type(extension: str) -> str:
    """
    ファイル拡張子から適切なmedia_typeを返す
    """
    media_types = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
    }
    return media_types.get(extension.lower(), "image/jpeg")


# 複数のpdf, image, 動画ファイルを入力してコンテンツを生成
async def generate_essay_json(
    files: list[str],
    uid: str,
    title: str,
    model_name: str = MODEL_NAME,
    bucket_name: str = BUCKET_NAME,
) -> dict:
    print("generate_essay_json started")  # デバッグ用
    print(f"tool_name: {tool_name}")  # デバッグ用
    print(f"tool_definition: {tool_definition}")  # デバッグ用

    content: list = []
    image_files: list[dict] = []

    try:
        client = AnthropicVertex(region=REGION, project_id=PROJECT_ID)

        # 全ファイルからのテキストを結合するための変数
        all_extracted_text = ""

        for file_name in files:
            if not uid or not uid.strip():
                raise ValueError("Invalid user ID")

            safe_uid = uid.strip().rstrip("/")
            file_name = unicodedata.normalize("NFC", f"{safe_uid}/{file_name}")
            print(f"Processing file: {file_name}")

            if await check_file_exists(bucket_name, file_name):
                print(f"File {file_name} exists in bucket {bucket_name}")

                if file_name.lower().endswith(".pdf"):
                    print(f"Extracting text from PDF: {file_name}")
                    extracted_text = await extract_text_from_pdf(bucket_name, file_name)
                    print(f"Extracted text length: {len(extracted_text)}")
                    # テキストを結合
                    all_extracted_text += f"\n=== {file_name} ===\n{extracted_text}"

                elif file_name.lower().endswith((".png", ".jpg", ".jpeg")):
                    print(f"Reading image file: {file_name}")
                    image_file = await read_file(bucket_name, file_name)

                    file_extension = file_name.split(".")[-1].lower()
                    image_files.append(
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": get_media_type(file_extension),
                                "data": image_file,
                            },
                        }
                    )

                    print(f"Added image file: {file_name} to image_files")

                elif file_name.lower().endswith(".mp4"):
                    logging.info(f"Converting {file_name} to mp3 format.")
                    if convert_mp4_to_mp3(bucket_name, file_name):
                        print(f"Successfully converted {file_name} to mp3 format.")
                        audio_text = extract_text_from_audio(bucket_name, file_name)
                        all_extracted_text += f"\n=== {file_name} ===\n{audio_text}"
                    else:
                        logging.error(f"Failed to convert {file_name} to mp3 format.")
                        raise InternalServerError(f"Failed to convert {file_name} to mp3 format.")

                elif file_name.lower().endswith((".mp3", ".wav")):
                    audio_text = extract_text_from_audio(bucket_name, file_name)
                    all_extracted_text += f"\n=== {file_name} ===\n{audio_text}"

        # まず抽出したテキストをコンテンツに追加
        if all_extracted_text:
            content.append({"type": "text", "text": f"講義テキスト:\n{all_extracted_text}"})
            print(f"Added extracted text to content (length: {len(all_extracted_text)})")

        # 画像ファイルを追加
        if image_files:
            for i, image in enumerate(image_files, 1):
                content.extend([{"type": "text", "text": f"Image {i}:"}, image])
            print(f"Added {len(image_files)} images to content")

        # 最後にプロンプトを追加
        content.append(
            {
                "type": "text",
                "text": f"上記の講義テキスト{title}の内容に基づいて、"
                + f"{tool_name}ツールを使用して問題を作成して下さい。",
            }
        )
        print("Added prompt to content")

        # デバッグ用にコンテンツの内容を出力
        print("Content structure:")
        for i, item in enumerate(content, 1):
            if item["type"] == "text":
                print(f"{i}. Type: text, Length: {len(item['text'])}")
            elif item["type"] == "image":
                image_info = item["source"]
                print(
                    f"{i}. Type: image, Format: {image_info['media_type']}, "
                    + f"Size: {len(image_info['data'])//1024}KB"
                )

        response = client.messages.create(
            max_tokens=4096,
            temperature=0.1,
            messages=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
            model=model_name,
            tools=[tool_definition],  # type: ignore
            tool_choice={"type": "tool", "name": tool_name},
        )

        # レスポンスの検証
        if response.content and len(response.content) > 0:
            if response.content[0].type == "tool_use":
                questions = response.content[0].input.get("questions", [])
                if any("<UNKNOWN>" in str(q) for q in questions):
                    logging.error("Invalid response received with <UNKNOWN> values")
                    raise ValueError("Failed to generate valid questions")

        print("generate_content_json finished")
        return response.to_dict()

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
    メイン関数。generate_essay_json関数をテストするためのコード
    """
    response: dict = await generate_essay_json(
        # ["kougi_sample.png", "kougi_sample2.png"],
        ["1_ソフトウェア工学の誕生.pdf"],
        uid="test_uid",
        title="test_title",
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
