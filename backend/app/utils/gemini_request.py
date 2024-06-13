import asyncio
import logging
import os

import vertexai
from dotenv import load_dotenv
from google.api_core.exceptions import GoogleAPIError, InvalidArgument, NotFound
from vertexai.generative_models import GenerationConfig, GenerativeModel, Part

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


# 複数のPDFファイルを入力してコンテンツを生成
async def generate_content(
    files: list[str],
    model_name: str = MODEL_NAME,
    generation_config: GenerationConfig = GENERATION_CONFIG,
    bucket_name: str = BUCKET_NAME,
) -> str:
    pdf_files: list[Part] = []
    # プロンプト（指示文）
    prompt = """
        - #role: あなたは、わかりやすく丁寧に教えることで評判の大学の「AI教授」です。
        - #input_files: 複数のファイルは、ソフトウェア工学の解説スライドです。
        - #instruction: 複数のpdfファイルを読み解いて、親しみやすい解説がついていて、
            誰もが読みたくなるような、わかりやすい整理ノートを日本語で作成して下さい。
        - #style: ビジュアル的にもわかりやすくするため、マークダウンで文字の大きさ、
            強調表示などのスタイルを工夫してください。
        - #condition1: 絵文字を使って、視覚的にもわかりやすくしてください。
        - #condition2: 途中に興味深いコラムを設けてください。
        - #condition3: 最後に用語解説のコーナーを設けてください。
        - #format: タイトルを付けて、8000文字程度のMarkdownで出力してください。
    """

    try:
        for file_name in files:
            # PDFファイルのURI
            pdf_file_uri = f"gs://{bucket_name}/{file_name}"
            # PDFファイルのパートを作成
            pdf_file = Part.from_uri(pdf_file_uri, mime_type="application/pdf")
            pdf_files.append(pdf_file)
    except NotFound as e:
        logging.error(f"File not found: {e}")
        raise
    except InvalidArgument as e:
        logging.error(f"Invalid file format: {e}")
        raise
    except GoogleAPIError as e:
        logging.error(f"Google API error: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error while reading PDF files: {e}")
        raise

    try:
        # モデルのインスタンスを作成
        model = GenerativeModel(model_name=model_name)

        # コンテンツリストを作成
        contents = pdf_files + [prompt]

        # 非同期でモデルにプロンプトとPDFを渡して応答を生成
        response = await asyncio.to_thread(
            model.generate_content, contents, generation_config=generation_config
        )
    except AttributeError as e:
        logging.error(f"Model attribute error: {e}")
        raise
    except TypeError as e:
        logging.error(f"Type error in model generation: {e}")
        raise
    except GoogleAPIError as e:
        logging.error(f"Google API error: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error during content generation: {e}")
        raise

    logging.info(f"Response: {response.text}")
    return response.text


# # テスト用のコード
# async def main() -> None:
#     await generate_content(["1_ソフトウェア工学の誕生.pdf", "5_アジャイルⅡ.pdf"])


# if __name__ == "__main__":
#     asyncio.run(main())