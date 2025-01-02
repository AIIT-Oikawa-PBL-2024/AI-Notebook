from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class Choice(BaseModel):
    choice_a: str = Field(..., description="選択肢A")
    choice_b: str = Field(..., description="選択肢B")
    choice_c: str = Field(..., description="選択肢C")
    choice_d: str = Field(..., description="選択肢D")


class ResponseData(BaseModel):
    question_id: str = Field(..., description="質問ID")
    question_text: str = Field(..., description="質問文")
    choices: Choice = Field(..., description="選択肢")
    user_selected_choice: str = Field(..., description="ユーザーが選択した選択肢")
    correct_choice: str = Field(..., description="正解の選択肢")
    is_correct: bool = Field(..., description="正解かどうかのフラグ")
    explanation: str = Field(..., description="解説文")


class SaveAnswerPayload(BaseModel):
    title: str = Field(..., description="問題集のタイトル")
    relatedFiles: List[str] = Field(..., description="関連ファイルのリスト")
    responses: List[ResponseData] = Field(..., description="ユーザーの回答データリスト")


class AnswerResponse(BaseModel):
    id: int = Field(..., description="回答のユニークID")
    title: str = Field(..., description="問題集のタイトル")
    related_files: List[str] = Field(..., description="関連ファイルのリスト")
    question_id: str = Field(..., description="質問ID")
    question_text: str = Field(..., description="質問文")
    choice_a: str = Field(..., description="選択肢A")
    choice_b: str = Field(..., description="選択肢B")
    choice_c: str = Field(..., description="選択肢C")
    choice_d: str = Field(..., description="選択肢D")
    user_selected_choice: str = Field(..., description="ユーザーが選択した選択肢")
    correct_choice: str = Field(..., description="正解の選択肢")
    is_correct: bool = Field(..., description="正解かどうかのフラグ")
    explanation: str = Field(..., description="解説文")
    user_id: str = Field(..., description="ユーザーID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    model_config = ConfigDict(from_attributes=True)


class DeleteResponse(BaseModel):
    message: str

    model_config = ConfigDict(
        json_schema_extra={"example": {"message": "回答が正常に削除されました。"}}
    )


class DeleteAnswersResult(BaseModel):
    deleted_ids: List[int] = Field(..., description="正常に削除された回答IDのリスト")
    not_found_ids: List[int] = Field(..., description="削除対象に存在しない回答IDのリスト")
    unauthorized_ids: List[int] = Field(..., description="ユーザーが所有していない回答IDのリスト")

    model_config = ConfigDict(from_attributes=True)


class BulkDeleteRequest(BaseModel):
    answer_ids: List[int]
