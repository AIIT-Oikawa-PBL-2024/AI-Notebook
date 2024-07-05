from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


# usersテーブルを定義
class User(Base):
    """
    Userモデルを定義します。

    :param id: ユーザーの一意の識別子
    :type id: int
    :param username: ユーザー名
    :type username: str
    :param email: ユーザーのメールアドレス
    :type email: str
    :param password: ユーザーのパスワード
    :type password: str
    :param files: ユーザーに関連するファイル
    :type files: list[File]
    :param outputs: ユーザーに関連する出力
    :type outputs: list[Output]
    :param notes: ユーザーに関連するノート
    :type notes: list[Note]
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(256), nullable=False, index=True)
    email = Column(String(256), nullable=False, unique=True, index=True)
    password = Column(String(256), nullable=False)

    files = relationship("File", back_populates="user", cascade="delete")
    outputs = relationship("Output", back_populates="user", cascade="delete")
    notes = relationship("Note", back_populates="user", cascade="delete")
