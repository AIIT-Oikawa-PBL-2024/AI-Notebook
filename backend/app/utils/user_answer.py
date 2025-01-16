import asyncio
import json
import logging
import os
from typing import Any, Callable, cast

from anthropic import AnthropicVertex
from dotenv import load_dotenv
from google.api_core.exceptions import (
    GoogleAPIError,
    InternalServerError,
)

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
tool_name = "print_user_answers"

description = """
- あなたは、わかりやすく丁寧に教えることで評判の大学の「AI教授」です。
- 入力値は問題文、回答例、解説、ユーザーの回答です。
- 5問の問題に対して、ユーザーの回答を採点し、解説とともに表示してください。
- 採点はA、B、C、D、Eの5段階で行ってください。
"""

tool_definition = {
    "name": "print_user_answers",
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
                        "scoring_result": {
                            "type": "string",
                            "description": "採点結果",
                        },
                        "explanation": {
                            "type": "string",
                            "description": "解説",
                        },
                    },
                    "required": [
                        "question_id",
                        "scoring_result",
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


async def generate_scoring_result_json(
    exercise: str,
    user_answers: list[str],
    uid: str,
    model_name: str = MODEL_NAME,
    bucket_name: str = BUCKET_NAME,
) -> dict:
    try:
        #

        # exerciseの内容を取得
        # JSON文字列を辞書型へ変換
        data = json.loads(exercise)

        # questionsリストの場所までアクセス
        questions = data["content"][0]["input"]["questions"]

        # question_idをキーに、question_text・answer・explanationをまとめた辞書を作成
        question_dict = {}
        for q in questions:
            q_id = q["question_id"]
            question_dict[q_id] = {
                "question_text": q["question_text"],
                "answer": q["answer"],
                "explanation": q["explanation"],
            }

        # 5個セットで取得したい場合
        # 質問が5個ある前提で、question_idに応じて抽出
        content = ""
        for i in range(1, 6):
            q_id = f"question_{i}"
            if q_id in question_dict:
                print(f"Question ID: {q_id}")
                print(f"Question Text: {question_dict[q_id]['question_text']}")
                print(f"Answer: {question_dict[q_id]['answer']}")
                print(f"Explanation: {question_dict[q_id]['explanation']}")
                print(f"User Answer: {user_answers[i-1]}")
                print("")
                # 抽出した内容をプロンプトに追加
                content += f"""
                問題文{q_id}: {question_dict[q_id]['question_text']}
                回答例{q_id}: {question_dict[q_id]['answer']}
                解説{q_id}: {question_dict[q_id]['explanation']}
                ユーザーの回答{q_id}: {user_answers[i-1]}
                """

        print("Added prompt to content")

        client = AnthropicVertex(region=REGION, project_id=PROJECT_ID)

        # ブロッキングする可能性のあるclient.messages.create呼び出しを非同期化
        # 型キャストを使ってラムダを定義
        create_message_call: Callable[[], Any] = cast(
            Callable[[], Any],
            lambda: client.messages.create(
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
            ),
        )
        response = await asyncio.to_thread(create_message_call)

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
