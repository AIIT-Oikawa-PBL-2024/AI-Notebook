import asyncio
import base64
import io
import logging
import os
import random
import unicodedata
from typing import Any, Callable, Dict, List, Optional, Protocol, Set, TypeVar

import fitz
from anthropic import AnthropicVertex
from dotenv import load_dotenv
from google.api_core.exceptions import GoogleAPIError, InternalServerError
from google.cloud import storage

from app.utils.convert_mp4_to_mp3 import convert_mp4_to_mp3
from app.utils.gemini_extract_text_from_audio import extract_text_from_audio

# 環境変数を読み込む
load_dotenv()

# プロジェクトIDとリージョンを環境変数から取得
PROJECT_ID: str = str(os.getenv("PROJECT_ID"))
REGION: str = "us-east5"  # リージョンは固定
MODEL_NAME: str = "claude-3-5-sonnet-v2@20241022"  # Claudeモデル名は固定
BUCKET_NAME: str = str(os.getenv("BUCKET_NAME"))

# ロギングの設定
logging.basicConfig(level=logging.INFO)

T = TypeVar("T")


class MessageContent(Protocol):
    type: str
    input: Dict[str, Any]


class Response(Protocol):
    content: List[MessageContent]

    def to_dict(self) -> Dict[str, Any]: ...


async def retry_create_with_backoff(
    create_func: Callable[[], T],
    max_retries: int = 3,
    base_delay: float = 30.0,
    max_delay: float = 300.0,
    exponential_base: float = 2.0,
    retryable_status_codes: Optional[Set[int]] = None,
) -> T:
    if retryable_status_codes is None:
        retryable_status_codes = {429, 503, 504}
    retry_count = 0

    while True:
        try:
            # 同期関数の実行を非同期にラップ
            return await asyncio.to_thread(create_func)
        except Exception as e:
            status_code: Optional[int] = None
            if hasattr(e, "status_code"):
                status_code = getattr(e, "status_code", None)
            elif "429" in str(e):
                status_code = 429

            if status_code in retryable_status_codes:
                retry_count += 1
                if retry_count > max_retries:
                    logging.error(f"Max retries ({max_retries}) exceeded. Final error: {e}")
                    raise e

                delay = min(base_delay * (exponential_base ** (retry_count - 1)), max_delay)
                jitter = random.uniform(0, 0.1 * delay)
                final_delay = delay + jitter

                logging.warning(
                    f"Received status {status_code}. Attempt {retry_count}/{max_retries}. "
                    f"Retrying in {final_delay:.2f} seconds..."
                )
                await asyncio.sleep(final_delay)
            else:
                logging.error(f"Non-retryable error occurred: {e}")
                raise e


# ツールの設定
tool_name: str = "print_essay_questions"

description: str = """
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

tool_definition: Dict[str, Any] = {
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

prompt: str = f"""
{tool_name} ツールのみを利用すること。
"""


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
    file_content: bytes = await asyncio.to_thread(blob.download_as_bytes)
    base64_encoded: str = base64.b64encode(file_content).decode("utf-8")
    return base64_encoded


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
    pdf_content: bytes = await asyncio.to_thread(blob.download_as_bytes)
    pdf_file = io.BytesIO(pdf_content)
    doc = await asyncio.to_thread(fitz.open, stream=pdf_file, filetype="pdf")
    extracted_text: str = ""
    for i, page in enumerate(doc):
        page_text: str = await asyncio.to_thread(page.get_text)
        extracted_text += f"\n# {i+1}ページ\n{page_text}"
    return extracted_text


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


async def generate_essay_json(
    files: List[str],
    uid: str,
    title: str,
    difficulty: str,
    model_name: str = MODEL_NAME,
    bucket_name: str = BUCKET_NAME,
) -> Dict[str, Any]:
    print("generate_essay_json started")
    print(f"tool_name: {tool_name}")
    print(f"tool_definition: {tool_definition}")

    content: List[Dict[str, Any]] = []
    image_files: List[Dict[str, Any]] = []
    difficulty_jp: str = await _convert_difficulty_in_japanese(difficulty)

    try:
        client = AnthropicVertex(region=REGION, project_id=PROJECT_ID)
        all_extracted_text: str = ""

        for file_name in files:
            if not uid or not uid.strip():
                raise ValueError("Invalid user ID")

            safe_uid: str = uid.strip().rstrip("/")
            normalized_file_name: str = unicodedata.normalize("NFC", f"{safe_uid}/{file_name}")
            print(f"Processing file: {normalized_file_name}")

            if await check_file_exists(bucket_name, normalized_file_name):
                print(f"File {normalized_file_name} exists in bucket {bucket_name}")

                if normalized_file_name.lower().endswith(".pdf"):
                    print(f"Extracting text from PDF: {normalized_file_name}")
                    extracted_text: str = await extract_text_from_pdf(
                        bucket_name, normalized_file_name
                    )
                    print(f"Extracted text length: {len(extracted_text)}")
                    all_extracted_text += f"\n=== {normalized_file_name} ===\n{extracted_text}"

                elif normalized_file_name.lower().endswith((".png", ".jpg", ".jpeg")):
                    print(f"Reading image file: {normalized_file_name}")
                    image_file: str = await read_file(bucket_name, normalized_file_name)
                    file_extension: str = normalized_file_name.split(".")[-1].lower()
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
                    print(f"Added image file: {normalized_file_name} to image_files")

                elif normalized_file_name.lower().endswith(".mp4"):
                    logging.info(f"Converting {normalized_file_name} to mp3 format.")
                    if await convert_mp4_to_mp3(bucket_name, normalized_file_name):
                        print(f"Successfully converted {normalized_file_name} to mp3 format.")
                        audio_text: str = await extract_text_from_audio(
                            bucket_name, normalized_file_name
                        )
                        all_extracted_text += f"\n=== {normalized_file_name} ===\n{audio_text}"
                    else:
                        logging.error(f"Failed to convert {normalized_file_name} to mp3 format.")
                        raise InternalServerError(
                            f"Failed to convert {normalized_file_name} to mp3 format."
                        )

                elif normalized_file_name.lower().endswith((".mp3", ".wav")):
                    audio_content: str = await extract_text_from_audio(
                        bucket_name, normalized_file_name
                    )
                    all_extracted_text += f"\n=== {normalized_file_name} ===\n{audio_content}"

        if all_extracted_text:
            content.append({"type": "text", "text": f"講義テキスト:\n{all_extracted_text}"})
            print(f"Added extracted text to content (length: {len(all_extracted_text)})")

        if image_files:
            for i, image in enumerate(image_files, 1):
                content.extend([{"type": "text", "text": f"Image {i}:"}, image])
            print(f"Added {len(image_files)} images to content")

        content.append(
            {
                "type": "text",
                "text": (
                    f"上記の講義テキスト{title}の内容に基づいて、"
                    f"{tool_name}ツールを使用して問題を作成して下さい。"
                    f"なお、問題の難易度は{difficulty_jp}としてください。"
                ),
            }
        )
        print("Added prompt to content")

        print("Content structure:")
        for i, item in enumerate(content, 1):
            if item["type"] == "text":
                print(f"{i}. Type: text, Length: {len(item['text'])}")
            elif item["type"] == "image":
                image_info = item["source"]
                print(
                    f"{i}. Type: image, Format: {image_info['media_type']}, "
                    f"Size: {len(image_info['data'])//1024}KB"
                )

        def create_request() -> Response:
            return client.messages.create(
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

        response = await retry_create_with_backoff(
            create_request, retryable_status_codes={429, 503, 504}
        )

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
        print(f"AttributeError: {e}")
        raise
    except TypeError as e:
        logging.error(f"Type error in model generation: {e}")
        print(f"TypeError: {e}")
        raise
    except InternalServerError as e:
        logging.error(f"Internal server error: {e}")
        print(f"InternalServerError: {e}")
        raise
    except GoogleAPIError as e:
        logging.error(f"Google API error: {e}")
        print(f"GoogleAPIError: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error during content generation: {e}")
        print(f"Unexpected error: {e}")
        raise


async def _convert_difficulty_in_japanese(original: str) -> str:
    if original == "easy":
        return "易しいレベル"
    elif original == "medium":
        return "普通レベル"
    elif original == "hard":
        return "難しいレベル"
    else:
        return ""


async def main() -> None:
    """
    メイン関数。generate_essay_json関数をテストするためのコード
    """
    response: Dict[str, Any] = await generate_essay_json(
        ["1_ソフトウェア工学の誕生.pdf"],
        uid="test_uid",
        title="test_title",
        difficulty="easy",
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
