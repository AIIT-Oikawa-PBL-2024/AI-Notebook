# app/models/file.py
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.exercises_files import exercise_file
from app.models.outputs_files import output_file


class File(Base):
    """
    ファイル情報を格納するためのSQLAlchemyモデルクラス。

    :param id: ファイルの一意の識別子
    :type id: int
    :param file_name: ファイルの名前
    :type file_name: str
    :param file_size: ファイルのサイズ（バイト単位）
    :type file_size: int
    :param user_id: ファイルを所有するユーザーのFirebase UID
    :type user_id: str
    :param created_at: ファイルの作成日時
    :type created_at: datetime
    :param exercises: このファイルに関連する練習問題のリスト
    :type exercises: list[Exercise]
    """

    __tablename__ = "files"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    file_name = Column(String(256), nullable=False, index=True)
    file_size = Column(Integer, nullable=False)
    user_id = Column(String(128), nullable=False, index=True)  # Firebase UIDの最大長に合わせて調整
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    # リレーションシップの定義
    exercises = relationship(
        "Exercise",
        secondary=exercise_file,  # 中間テーブルのオブジェクトを指定
        back_populates="files",
    )

    # リレーションシップの定義
    outputs = relationship(
        "Output",
        secondary=output_file,  # 中間テーブルのオブジェクトを指定
        back_populates="files",
    )
