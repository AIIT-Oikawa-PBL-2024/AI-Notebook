"""Add updated_at column to files

Revision ID: efc4b7e31981
Revises: 7a2fc39f5b0b
Create Date: 2024-11-27 11:29:29.529923

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'efc4b7e31981'
down_revision: Union[str, None] = '7a2fc39f5b0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('files', sa.Column('updated_at', sa.DateTime(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('files', 'updated_at')
    # ### end Alembic commands ###
