from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FileBase(BaseModel):
    """
    基本的なファイル情報を表すモデル。

    Attributes:
        file_name (str): ファイルの名前。
        file_size (int): ファイルのサイズ。
    """

    file_name: str
    file_size: int


class FileCreate(FileBase):
    """
    ファイル作成時の情報を表すモデル。

    Attributes:
        user_id (str): ユーザーID。
        created_at (datetime): 作成日時。
    """

    user_id: str
    created_at: datetime


class File(FileBase):
    """
    作成されたファイルの情報を表すモデル。

    Attributes:
        id (int): ファイルのID。
        user_id (str): ユーザーID。
        created_at (datetime): 作成日時。
    """

    id: int
    user_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
