import os

import vertexai
from dotenv import load_dotenv
from vertexai.generative_models import GenerativeModel, Part

# 環境変数を読み込む
load_dotenv()

# プロジェクトIDとリージョンを環境変数から取得
PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")
MODEL_NAME = "gemini-1.5-pro-001"

# Vertex AIを初期化
vertexai.init(project=PROJECT_ID, location=REGION)

# PDFファイルのURI
pdf_file_uri = "gs://ai-notebook-test001/5_アジャイルⅡ.pdf"

# プロンプト（指示文）
prompt = """
あなたは、わかりやすく丁寧に教えることで評判の大学教授です。
ソフトウェア工学についてのスライド資料と解説です。
この資料と解説に基づいて、わかりやすく、親しみやすい解説がついていて、誰もが読みたくなるような整理ノートを作成して下さい。
ビジュアル的にもわかりやすくするため、マークダウンで文字の大きさ、強調表示などのスタイルを作成して、スライド資料の図を複数挿入できるようにスライドのページと配置を指定してください。
また、コラムや用語解説を複数つけて、興味を持てるようにしてください。
最後に選択式と穴埋め式の練習問題を付けてください。
問題の解答は、最後に別枠で記載してください。
出力のファイル形式は、マークダウンのファイルで出力してください。
"""


# コンテンツ生成関数
def generate_content(pdf_file_uri: str, prompt: str) -> str:
    # モデルのインスタンスを作成
    model = GenerativeModel(model_name=MODEL_NAME)
    # PDFファイルのパートを作成
    pdf_file = Part.from_uri(pdf_file_uri, mime_type="application/pdf")
    # コンテンツリストを作成
    contents = [pdf_file, prompt]
    # コンテンツを生成
    response = model.generate_content(contents)
    # 生成されたテキストを出力
    print(response.text)
    return response.text
