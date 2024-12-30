"""upgrade_answers_table

Revision ID: 22e84fe86fcb
Revises: 0466229c861e
Create Date: 2024-12-29 15:37:02.843803

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "22e84fe86fcb"
down_revision: Union[str, None] = "0466229c861e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # まずテーブルを作成
    op.create_table(
        "answers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=False),  # 最初からString型で作成
        sa.Column("related_files", sa.JSON(), nullable=False),
        sa.Column("question_id", sa.String(length=256), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("choice_a", sa.Text(), nullable=False),
        sa.Column("choice_b", sa.Text(), nullable=False),
        sa.Column("choice_c", sa.Text(), nullable=False),
        sa.Column("choice_d", sa.Text(), nullable=False),
        sa.Column("user_selected_choice", sa.String(length=256), nullable=False),
        sa.Column("correct_choice", sa.String(length=256), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # インデックスを作成
    op.create_index(op.f("ix_answers_id"), "answers", ["id"], unique=False)
    op.create_index(op.f("ix_answers_title"), "answers", ["title"], unique=False)
    op.create_index(op.f("ix_answers_user_id"), "answers", ["user_id"], unique=False)
    op.create_index(op.f("ix_answers_question_id"), "answers", ["question_id"], unique=False)


def downgrade() -> None:
    # すべてのインデックスを削除
    op.drop_index(op.f("ix_answers_question_id"), table_name="answers")
    op.drop_index(op.f("ix_answers_user_id"), table_name="answers")
    op.drop_index(op.f("ix_answers_title"), table_name="answers")
    op.drop_index(op.f("ix_answers_id"), table_name="answers")

    # テーブルを削除
    op.drop_table("answers")
