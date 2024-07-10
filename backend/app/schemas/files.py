from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FileBase(BaseModel):
    """
    基本的なファイル情報を表すモデル。

    :Attributes:
        file_name (str): ファイルの名前。
        file_size (int): ファイルのサイズ。
    """

    file_name: str
    file_size: int


class FileCreate(FileBase):
    """
    ファイル作成時の情報を表すモデル。

    :Attributes:
        user_id (int): ユーザーID。
        created_at (datetime): 作成日時。
    """

    user_id: int
    created_at: datetime


# ファイル作成時のレスポンス
class File(FileCreate):
    """
    作成されたファイルの情報を表すモデル。

    :Attributes:
        id (int): ファイルのID。
    """

    id: int

    model_config = ConfigDict(from_attributes=True)
