"""create exercise table

Revision ID: 93f95e7aa12b
Revises: 41b7289ead85
Create Date: 2024-11-01 15:35:01.924754

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "93f95e7aa12b"
down_revision: Union[str, None] = "41b7289ead85"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "exercises",  # テーブル名はモデルと同じ exercises
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True, index=True),
        sa.Column("user_id", sa.String(128), nullable=False, index=True),
        sa.Column("response", sa.TEXT(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("exercise_type", sa.String(128), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("exercises")
