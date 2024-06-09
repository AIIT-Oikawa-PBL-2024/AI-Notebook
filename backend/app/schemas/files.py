from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FileBase(BaseModel):
    file_name: str
    file_size: int


class FileCreate(FileBase):
    user_id: int
    created_at: datetime


# ファイル作成時のレスポンス
class File(FileCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
