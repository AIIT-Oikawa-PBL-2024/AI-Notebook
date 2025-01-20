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
from google.api_core.exceptions import (
    GoogleAPIError,
    InternalServerError,
)
from google.cloud import storage

from app.utils.convert_mp4_to_mp3 import convert_mp4_to_mp3
from app.utils.gemini_extract_text_from_audio import extract_text_from_audio


# プロトコルの定義
class MessageContent(Protocol):
    type: str
    input: Dict[str, Any]


class Response(Protocol):
    content: List[MessageContent]

    def to_dict(self) -> Dict[str, Any]: ...


# 環境変数を読み込む
load_dotenv()

# プロジェクトIDとリージョンを環境変数から取得
PROJECT_ID = str(os.getenv("PROJECT_ID"))
REGION = "us-east5"  # リージョンは固定
MODEL_NAME = "claude-3-5-sonnet-v2@20241022"  # Claudeモデル名は固定
BUCKET_NAME: str = str(os.getenv("BUCKET_NAME"))

# ロギングの設定
logging.basicConfig(level=logging.INFO)

T = TypeVar("T")


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
            return await asyncio.to_thread(create_func)
        except Exception as e:
            status_code: Any = None
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
tool_name = "print_multiple_choice_questions"

description = """
- あなたは、わかりやすく丁寧に教えることで評判の大学の「AI教授」です。
- 入力された大学院の講義テキストの内容に基づいて、練習問題を作成してください。
- "4択の選択問題"と"正解"と"解説"のセットを10問作成してください。
- 重要な概念や用語を確認できる問題を作成してください。
- 以下のruleに従って作成してください。

<rule>
- 入力テキストの内容に基づいて、4択の選択問題を10問作成してください。
- 各問題には、問題文、4つの選択肢、正解、詳しい解説を含めてください。
- 簡単な問題から難しい問題まで、バランスの取れた問題セットを作成してください。
- 重要なキーワードや概念を理解・記憶できる良問を心がけてください。
- 問題のフォーマットは以下の形式に従ってください：
  question_[番号]: 問題文
  choice_a: 選択肢A
  choice_b: 選択肢B
  choice_c: 選択肢C
  choice_d: 選択肢D
  answer: 正解の選択肢
  explanation: 解説
</rule>
"""

tool_definition = {
    "name": "print_multiple_choice_questions",
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
                        "choices": {
                            "type": "object",
                            "properties": {
                                "choice_a": {
                                    "type": "string",
                                    "description": "選択肢A",
                                },
                                "choice_b": {
                                    "type": "string",
                                    "description": "選択肢B",
                                },
                                "choice_c": {
                                    "type": "string",
                                    "description": "選択肢C",
                                },
                                "choice_d": {
                                    "type": "string",
                                    "description": "選択肢D",
                                },
                            },
                            "required": [
                                "choice_a",
                                "choice_b",
                                "choice_c",
                                "choice_d",
                            ],
                        },
                        "answer": {
                            "type": "string",
                            "description": "正解の選択肢ID (例: choice_c)",
                            "enum": [
                                "choice_a",
                                "choice_b",
                                "choice_c",
                                "choice_d",
                            ],
                        },
                        "explanation": {
                            "type": "string",
                            "description": "解説文",
                        },
                    },
                    "required": [
                        "question_id",
                        "question_text",
                        "choices",
                        "answer",
                        "explanation",
                    ],
                },
                "minItems": 10,
                "maxItems": 10,
            }
        },
        "required": ["questions"],
    },
}

prompt = f"""
{tool_name} ツールのみを利用すること。
"""


async def check_file_exists(bucket_name: str, file_name: str) -> bool:
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    return blob.exists()


async def read_file(bucket_name: str, file_name: str) -> str:
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    file_content = await asyncio.to_thread(blob.download_as_bytes)
    base64_encoded = base64.b64encode(file_content).decode("utf-8")
    return base64_encoded


async def extract_text_from_pdf(bucket_name: str, file_name: str) -> str:
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    pdf_content = await asyncio.to_thread(blob.download_as_bytes)
    pdf_file = io.BytesIO(pdf_content)
    doc = await asyncio.to_thread(fitz.open, stream=pdf_file, filetype="pdf")
    extracted_text = ""
    for i, page in enumerate(doc):
        page_text = await asyncio.to_thread(page.get_text)
        extracted_text += f"\n# {i+1}ページ\n{page_text}"
    return extracted_text


def get_media_type(extension: str) -> str:
    media_types = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
    }
    return media_types.get(extension.lower(), "image/jpeg")


async def generate_content_json(
    files: list[str],
    uid: str,
    title: str,
    difficulty: str,
    model_name: str = MODEL_NAME,
    bucket_name: str = BUCKET_NAME,
) -> dict:
    print("generate_content_json started")  # デバッグ用

    content: list = []
    image_files: list[dict] = []
    difficulty_jp = await _convert_difficulty_in_japanese(difficulty)

    try:
        client = AnthropicVertex(region=REGION, project_id=PROJECT_ID)
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
                    if await convert_mp4_to_mp3(bucket_name, file_name):
                        print(f"Successfully converted {file_name} to mp3 format.")
                        audio_text = await extract_text_from_audio(bucket_name, file_name)
                        all_extracted_text += f"\n=== {file_name} ===\n{audio_text}"
                    else:
                        logging.error(f"Failed to convert {file_name} to mp3 format.")
                        raise InternalServerError(f"Failed to convert {file_name} to mp3 format.")

                elif file_name.lower().endswith((".mp3", ".wav")):
                    audio_text = await extract_text_from_audio(bucket_name, file_name)
                    all_extracted_text += f"\n=== {file_name} ===\n{audio_text}"

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
                "text": f"上記の講義テキスト{title}の内容に基づいて、"
                + f"{tool_name}ツールを使用して問題を作成して下さい。"
                + f"なお、問題の難易度は{difficulty_jp}としてください。",
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
                    + f"Size: {len(image_info['data'])//1024}KB"
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


async def generate_similar_questions_json(
    files: list[str],
    uid: str,
    title: str,
    answers: list[str],
    model_name: str = MODEL_NAME,
    bucket_name: str = BUCKET_NAME,
) -> dict:
    print("generate_content_json started")  # デバッグ用

    content: list = []
    image_files: list[dict] = []

    try:
        client = AnthropicVertex(region=REGION, project_id=PROJECT_ID)
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
                    if await convert_mp4_to_mp3(bucket_name, file_name):
                        print(f"Successfully converted {file_name} to mp3 format.")
                        audio_text = await extract_text_from_audio(bucket_name, file_name)
                        all_extracted_text += f"\n=== {file_name} ===\n{audio_text}"
                    else:
                        logging.error(f"Failed to convert {file_name} to mp3 format.")
                        raise InternalServerError(f"Failed to convert {file_name} to mp3 format.")

                elif file_name.lower().endswith((".mp3", ".wav")):
                    audio_text = await extract_text_from_audio(bucket_name, file_name)
                    all_extracted_text += f"\n=== {file_name} ===\n{audio_text}"

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
                "text": f"上記の講義テキスト{title}の内容に基づいて、"
                + (
                    "AIが作成した選択問題、ユーザーの解答、正解、正誤、"
                    "解説が10問分、以下に与えられています。\n"
                )
                + f"{answers}\n"
                + (
                    "ユーザーの解答が誤っている問題の分野を見つけて、"
                    "講義テキストから類似問題を作成して下さい。"
                )
                + "すでにAIが作成した問題と重複しないように注意して下さい。"
                + "ユーザーが解答を誤った苦手な分野を集中的に克服することが目的です。"
                + "AIが作成した問題、ユーザーの解答の正誤、解説を参考にして、"
                + f"{tool_name}ツールを使用して問題を作成して下さい。",
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
                    + f"Size: {len(image_info['data'])//1024}KB"
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
