import asyncio
import logging
import os
import random
from typing import Any, Callable, List, Optional, Protocol, Set, TypeVar

import vertexai
from dotenv import load_dotenv
from google.api_core.exceptions import (
    InternalServerError,
)
from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    Part,
)


# プロトコルの定義
class Response(Protocol):
    text: str


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


async def extract_text_from_audio(
    bucket_name: str,
    file_name: str,
    model_name: str = MODEL_NAME,
    generation_config: GenerationConfig = GENERATION_CONFIG,
) -> str:
    """
    音声ファイルからテキストを抽出する非同期関数

    Args:
        bucket_name (str): GCSバケット名
        file_name (str): 音声ファイル名
        model_name (str): 使用するモデル名
        generation_config (GenerationConfig): 生成設定

    Returns:
        str: 抽出されたテキスト
    """

    print("extract_text_from_audio started!!!")
    # プロンプト（指示文）
    prompt = """
        - #role: あなたは、学術・教育分野における高精度な要約のプロフェッショナルです。。
        - #input_files: 添付のファイルは、大学院の講義の音声ファイルです。
        - #instruction: 音声ファイルの内容を、8000文字程度の正確で読みやすい文章に要約してください。
            学術的な正確性と可読性の両立を目指してください。
        - #condition1: フィラーや繋ぎ言葉は全て除外してください。
        - #condition2: 固有名詞、数値や日付、専門用語は正確に記録してください。
        - #condition3: 可能な限り自然な日本語に整形してください。
        - #condition4: 会話の流れや論理展開を損なわないように注意してください。
        - #condition5: 専門的な内容の場合、その分野の専門用語や表現は維持してください。
        - #format: 8000文字程度の要約テキストとして出力してください。
    """
    print(f"prompt: {prompt}")  # デバッグ用
    audio_files: List[Part] = []
    try:
        # オーディオ設定
        if file_name.lower().endswith(".mp4"):
            mp3_file_name = file_name.replace(".mp4", ".mp3")
            audio_gcs_uri = f"gs://{bucket_name}/mp3/{mp3_file_name}"
            audio_file = Part.from_uri(audio_gcs_uri, mime_type="audio/mp3")
        elif file_name.lower().endswith(".mp3"):
            audio_gcs_uri = f"gs://{bucket_name}/{file_name}"
            audio_file = Part.from_uri(audio_gcs_uri, mime_type="audio/mp3")
        elif file_name.lower().endswith(".wav"):
            audio_gcs_uri = f"gs://{bucket_name}/{file_name}"
            audio_file = Part.from_uri(audio_gcs_uri, mime_type="audio/wav")
        else:
            raise ValueError("Unsupported audio file format.")

        audio_files.append(audio_file)

        # モデルのインスタンスを作成
        model = GenerativeModel(model_name=model_name)

        # コンテンツリストを作成
        contents = audio_files + [prompt]

        def create_request() -> Response:
            return model.generate_content(
                contents,
                generation_config=generation_config,
                stream=False,
            )

        response = await retry_create_with_backoff(create_request)

        # レスポンスからテキストを取得
        return response.text

    except Exception as e:
        logging.error(f"音声の文字起こしエラー: {str(e)}", exc_info=True)
        raise InternalServerError(f"音声の文字起こしエラー: {str(e)}") from None
