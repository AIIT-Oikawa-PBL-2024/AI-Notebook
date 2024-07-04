from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    """
    ユーザーの基本情報を表すモデル。

    Attributes:
        username (str): ユーザー名。
        email (str): メールアドレス。
    """

    username: str
    email: str


class UserCreate(UserBase):
    """
    新しいユーザーを作成するためのモデル。

    Attributes:
        password (str): パスワード。
    """

    password: str


class UserCreateResponse(UserCreate):
    """
    新しいユーザー作成のレスポンスモデル。

    Attributes:
        id (int): ユーザーID。
    """

    id: int

    model_config = ConfigDict(from_attributes=True)


class User(UserBase):
    """
    ユーザー情報を表すモデル。

    Attributes:
        id (int): ユーザーID。
    """

    id: int

    model_config = ConfigDict(from_attributes=True)
