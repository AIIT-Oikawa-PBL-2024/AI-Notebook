import asyncio
import json
import logging
import os
import random
import unicodedata
from typing import Any, AsyncGenerator, Callable, Iterator, Optional, Set, TypeVar

import vertexai
from dotenv import load_dotenv
from google.api_core.exceptions import (
    GoogleAPIError,
    InternalServerError,
    InvalidArgument,
    NotFound,
)
from google.cloud import storage
from vertexai.generative_models import (
    GenerationConfig,
    GenerationResponse,
    GenerativeModel,
    Part,
)

from app.utils.convert_mp4_to_mp3 import convert_mp4_to_mp3

# 環境変数を読み込む
load_dotenv()

# プロジェクトIDとリージョンを環境変数から取得
PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")
MODEL_NAME = "gemini-1.5-pro-001"
BUCKET_NAME: str = str(os.getenv("BUCKET_NAME"))

# 生成モデルのパラメータを設定
GENERATION_CONFIG = GenerationConfig(max_output_tokens=8192, temperature=0)

# Vertex AIを初期化
vertexai.init(project=PROJECT_ID, location=REGION)

# ロギングの設定
logging.basicConfig(level=logging.INFO)

T = TypeVar("T")


async def retry_create_with_backoff(
    create_func: Callable[[], T],
    max_retries: int = 3,
    base_delay: float = 10.0,
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


# Google Cloud Storageでファイルが存在するかチェック
def check_file_exists(bucket_name: str, file_name: str) -> bool:
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    return blob.exists()


# 複数のPDF, imageファイルを入力してコンテンツを生成
async def generate_content_stream(
    files: list[str],
    uid: str,
    style: str,
    model_name: str = MODEL_NAME,
    generation_config: GenerationConfig = GENERATION_CONFIG,
    bucket_name: str = BUCKET_NAME,
) -> AsyncGenerator[GenerationResponse, None]:
    pdf_files: list[Part] = []
    image_files: list[Part] = []
    mp3_files: list[Part] = []
    wav_files: list[Part] = []

    file_names = files
    file_list_str = ", ".join(
        [
            f"`{os.path.splitext(file_name)[0]}.mp3`"
            if file_name.endswith(".mp4")
            else f"`{file_name}`"
            for file_name in file_names
        ]
    )

    casual_prompt = f"""
        - #role: あなたは、わかりやすく丁寧に教えることで評判の大学の「AI教授」です。
        - #input_files: {file_list_str} は、大学院の講義資料です。
        - #instruction: {file_list_str} のファイルを読み解いて、
            親しみやすい解説がついて、誰もが読みたくなるような、
            わかりやすい整理ノートを日本語で作成して下さい。
            imageファイルが複数ある場合、それぞれの画像に対して解説を行ってください。
        - #style: ビジュアル的にもわかりやすくするため、マークダウンで文字の大きさ、
            強調表示などのスタイルを追加してください。
        - #condition1: "絵文字"を使って、視覚的にもわかりやすくしてください。
        - #condition2: ”表形式”は禁止します。”箇条書き”を使用してください。
        - #condition3: URLを含むリンクを表示することは禁止します。
        - #condition4: 画像ファイルを挿入することは禁止します。
        - #condition5: 興味深い"コラム"の欄を設けてください。
        - #condition6: 最後に"用語解説"の一覧を箇条書き形式で表示してください。
        - #format: タイトルを付けて、8000文字程度のMarkdownで出力してください。
    """

    simple_prompt = f"""
        - #role: あなたは、わかりやすく丁寧に教えることで評判の大学の「AI教授」です。
        - #input_files: {file_list_str} は、大学院の講義資料です。
        - #instruction: {file_list_str} のファイルを読み解いて、
            読みやすい解説がついて、誰もが理解できる整理ノートを日本語で作成して下さい。
            imageファイルが複数ある場合、それぞれの画像に対して解説を行ってください。
        - #style: ビジュアル的にもわかりやすくするため、マークダウンで文字の大きさ、
            強調表示などのスタイルを追加してください。
        - #condition1: "絵文字"を使わずに、シンプルな表現にしてください。
        - #condition2: ”表形式”は禁止します。”箇条書き”を使用してください。
        - #condition3: URLを含むリンクを表示することは禁止します。
        - #condition4: 画像ファイルを挿入することは禁止します。
        - #condition5: 興味深い"コラム"の欄を設けてください。
        - #condition6: 最後に"用語解説"の一覧を箇条書き形式で表示してください。
        - #format: タイトルを付けて、8000文字程度のMarkdownで出力してください。
    """

    if style == "casual":
        prompt = casual_prompt
    else:
        prompt = simple_prompt

    logging.info(f"Prompt: {prompt}")
    try:
        for file_name in files:
            if file_name:
                if not uid or not uid.strip():
                    raise ValueError("Invalid user ID")
                safe_uid = uid.strip().rstrip("/")
                file_name = unicodedata.normalize("NFC", f"{safe_uid}/{file_name}")
            if check_file_exists(bucket_name, file_name):
                if file_name.endswith(".pdf"):
                    pdf_file_uri = f"gs://{bucket_name}/{file_name}"
                    pdf_file = Part.from_uri(pdf_file_uri, mime_type="application/pdf")
                    pdf_files.append(pdf_file)
                elif file_name.endswith(".jpg") or file_name.endswith(".jpeg"):
                    image_file_uri = f"gs://{bucket_name}/{file_name}"
                    image_file = Part.from_uri(image_file_uri, mime_type="image/jpeg")
                    image_files.append(image_file)
                elif file_name.endswith(".png"):
                    image_file_uri = f"gs://{bucket_name}/{file_name}"
                    image_file = Part.from_uri(image_file_uri, mime_type="image/png")
                    image_files.append(image_file)
                elif file_name.endswith(".mp4"):
                    if await convert_mp4_to_mp3(bucket_name, file_name):
                        mp3_file_name = file_name.replace(".mp4", ".mp3")
                        mp3_file_url = f"gs://{bucket_name}/mp3/{mp3_file_name}"
                        mp3_file = Part.from_uri(mp3_file_url, mime_type="audio/mp3")
                        mp3_files.append(mp3_file)
                    else:
                        logging.error(f"Failed to convert {file_name} to mp3 format.")
                        raise InternalServerError(f"Failed to convert {file_name} to mp3 format.")
                elif file_name.endswith(".mp3"):
                    mp3_file_url = f"gs://{bucket_name}/{file_name}"
                    mp3_file = Part.from_uri(mp3_file_url, mime_type="audio/mp3")
                    mp3_files.append(mp3_file)
                elif file_name.endswith(".wav"):
                    wav_file_url = f"gs://{bucket_name}/{file_name}"
                    wav_file = Part.from_uri(wav_file_url, mime_type="audio/wav")
                    wav_files.append(wav_file)
                else:
                    logging.error(
                        f"Invalid file format: {file_name}. "
                        + "Only PDF and image and audio files are supported."
                    )
                    raise InvalidArgument(
                        f"Invalid file format: {file_name}. "
                        + "Only PDF and image and audio files are supported."
                    )
            else:
                logging.error(f"File {file_name} does not exist in the bucket {bucket_name}.")
                raise NotFound(f"File {file_name} does not exist in the bucket {bucket_name}.")
        logging.info(f"Files: {pdf_files + image_files} are read.")

    except InternalServerError as e:
        logging.error(f"Internal server error: {e}")
        raise
    except GoogleAPIError as e:
        logging.error(f"Google API error: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error while reading files: {e}")
        raise

    try:
        # モデルのインスタンスを作成
        model = GenerativeModel(model_name=model_name)

        # コンテンツリストを作成
        contents = pdf_files + image_files + mp3_files + wav_files + [prompt]

        def create_request() -> Iterator[GenerationResponse]:
            return model.generate_content(
                contents,
                generation_config=generation_config,
                stream=True,
            )

        # リトライロジックを適用して同期的にコンテンツを生成
        sync_response = await retry_create_with_backoff(create_request)

        for content in sync_response:
            yield content

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


# 429エラーテスト用のコード
async def process_single_request(request_id: int) -> None:
    try:
        response: AsyncGenerator = generate_content_stream(
            ["1_ソフトウェア工学の誕生.pdf"], "test_uid", "casual"
        )
        async for content in response:
            content_dict = content.to_dict()
            json_string = json.dumps(content_dict)
            data = json.loads(json_string)
            text_value = data["candidates"][0]["content"]["parts"][0]["text"]
            print(f"Request {request_id}: {text_value[:50]}...")  # 最初の50文字だけ表示
    except Exception as e:
        print(f"Request {request_id} failed with error: {str(e)}")


async def main() -> None:
    # 同時に実行するリクエスト数
    num_requests = 10

    # すべてのリクエストを並列で実行
    tasks = []
    for i in range(num_requests):
        tasks.append(process_single_request(i))

    print(f"Starting {num_requests} parallel requests...")
    await asyncio.gather(*tasks)
    print("All requests completed")


if __name__ == "__main__":
    # ログレベルを設定
    logging.basicConfig(level=logging.INFO)

    # メイン関数を実行
    asyncio.run(main())
