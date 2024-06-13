from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OutputBase(BaseModel):
    output: str


class OutputCreate(OutputBase):
    user_id: int
    created_at: datetime


# 学習帳作成時のレスポンス
class Output(OutputCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
