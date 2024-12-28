from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, Text

from app.database import Base


class Answer(Base):
    """
    ユーザーの回答データを保存するためのモデル
    """

    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(256), index=True, nullable=False)
    related_files = Column(JSON, nullable=False)
    question_id = Column(String(256), index=True, nullable=False)
    question_text = Column(Text, nullable=False)
    choice_a = Column(Text, nullable=False)
    choice_b = Column(Text, nullable=False)
    choice_c = Column(Text, nullable=False)
    choice_d = Column(Text, nullable=False)
    user_selected_choice = Column(String(256), nullable=False)
    correct_choice = Column(
        String(256),
        nullable=False,
    )
    is_correct = Column(
        Boolean,
        nullable=False,
    )
    explanation = Column(Text, nullable=False)
    user_id = Column(
        String(128),
        nullable=False,
        index=True,
    )
    created_at = Column(
        DateTime,
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
    )
