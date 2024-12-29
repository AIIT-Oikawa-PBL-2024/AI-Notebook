"""add answers table

Revision ID: 5dac468e846d
Revises: 0466229c861e
Create Date: 2024-12-26 15:16:16.597705

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5dac468e846d"
down_revision: Union[str, None] = "0466229c861e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # まずテーブルを作成
    op.create_table(
        "answers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        # 他に必要なカラムがあれば追加
        sa.PrimaryKeyConstraint("id"),
    )

    # その後でインデックスを作成
    op.create_index(op.f("ix_answers_title"), "answers", ["title"], unique=False)
    op.create_index(op.f("ix_answers_user_id"), "answers", ["user_id"], unique=False)


def downgrade() -> None:
    # 逆の順序で削除
    op.drop_index(op.f("ix_answers_user_id"), table_name="answers")
    op.drop_index(op.f("ix_answers_title"), table_name="answers")
    op.drop_table("answers")
