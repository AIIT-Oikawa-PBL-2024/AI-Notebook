import asyncio
import json
import logging
import os
import unicodedata
from typing import AsyncGenerator

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
    model_name: str = MODEL_NAME,
    generation_config: GenerationConfig = GENERATION_CONFIG,
    bucket_name: str = BUCKET_NAME,
) -> AsyncGenerator[GenerationResponse, None]:
    pdf_files: list[Part] = []
    image_files: list[Part] = []
    # プロンプト（指示文）
    prompt = """
        - #role: あなたは、わかりやすく丁寧に教えることで評判の大学の「AI教授」です。
        - #input_files: 複数のファイルは、ソフトウェア工学の解説スライドです。
        - #instruction: 複数のpdf, imageファイルを読み解いて、親しみやすい解説がついて、
            誰もが読みたくなるような、わかりやすい整理ノートを日本語で作成して下さい。
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

    try:
        for file_name in files:
            # ブロブ名を正規化
            if file_name:
                # ユーザーIDの検証
                if not uid or not uid.strip():
                    raise ValueError("Invalid user ID")

                # パスの正規化
                safe_uid = uid.strip().rstrip("/")
                file_name = unicodedata.normalize("NFC", f"{safe_uid}/{file_name}")
            # ファイルがGCSに存在するかチェック
            if check_file_exists(bucket_name, file_name):
                if file_name.endswith(".pdf"):
                    # PDFファイルのURI
                    pdf_file_uri = f"gs://{bucket_name}/{file_name}"
                    # PDFファイルのパートを作成
                    pdf_file = Part.from_uri(pdf_file_uri, mime_type="application/pdf")
                    pdf_files.append(pdf_file)
                elif file_name.endswith(".jpg") or file_name.endswith(".jpeg"):
                    # imageファイルのURI
                    image_file_uri = f"gs://{bucket_name}/{file_name}"
                    # imageファイルのパートを作成
                    image_file = Part.from_uri(image_file_uri, mime_type="image/jpeg")
                    image_files.append(image_file)
                elif file_name.endswith(".png"):
                    # imageファイルのURI
                    image_file_uri = f"gs://{bucket_name}/{file_name}"
                    # imageファイルのパートを作成
                    image_file = Part.from_uri(image_file_uri, mime_type="image/png")
                    image_files.append(image_file)
                else:
                    logging.error(
                        f"Invalid file format: {file_name}. "
                        + "Only PDF and image files are supported."
                    )
                    raise InvalidArgument(
                        f"Invalid file format: {file_name}. "
                        + "Only PDF and image files are supported."
                    )
            else:
                logging.error(
                    f"File {file_name} does not exist in the bucket {bucket_name}."
                )
                raise NotFound(
                    f"File {file_name} does not exist in the bucket {bucket_name}."
                )
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
        contents = pdf_files + image_files + [prompt]

        # 同期関数を非同期にラップする
        sync_response = await asyncio.to_thread(
            model.generate_content,
            contents,
            generation_config=generation_config,
            stream=True,
        )

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


# テスト用のコード
async def main() -> None:
    response: AsyncGenerator = generate_content_stream(
        ["kougi_sample.png", "kougi_sample2.png"], "test_uid"
    )
    async for content in response:
        # まず辞書形式に変換
        content_dict = content.to_dict()

        # 辞書をJSON文字列に変換
        json_string = json.dumps(content_dict)

        # JSON文字列をパース
        data = json.loads(json_string)

        # textの値を出力
        text_value = data["candidates"][0]["content"]["parts"][0]["text"]
        print(text_value, end="")


if __name__ == "__main__":
    asyncio.run(main())
