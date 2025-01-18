"""make difficulty nullable

Revision ID: e19876d7c6c7
Revises: 112b4c0f26dc
Create Date: 2025-01-16 09:00:59.245586

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'e19876d7c6c7'
down_revision: Union[str, None] = '112b4c0f26dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.String(length=128), nullable=False),
    sa.Column('title', sa.String(length=256), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notes_id'), 'notes', ['id'], unique=False)
    op.create_index(op.f('ix_notes_title'), 'notes', ['title'], unique=False)
    op.create_index(op.f('ix_notes_user_id'), 'notes', ['user_id'], unique=False)
    op.create_table('exercise_file',
    sa.Column('exercise_id', sa.Integer(), nullable=False),
    sa.Column('file_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ),
    sa.ForeignKeyConstraint(['file_id'], ['files.id'], ),
    sa.PrimaryKeyConstraint('exercise_id', 'file_id')
    )
    op.create_table('output_file',
    sa.Column('output_id', sa.Integer(), nullable=False),
    sa.Column('file_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['file_id'], ['files.id'], ),
    sa.ForeignKeyConstraint(['output_id'], ['outputs.id'], ),
    sa.PrimaryKeyConstraint('output_id', 'file_id')
    )
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_table('users')
    op.add_column('exercises', sa.Column('title', sa.String(length=100), nullable=False))
    op.add_column('exercises', sa.Column('difficulty', sa.String(length=10), nullable=True))
    op.add_column('files', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.alter_column('files', 'user_id',
               existing_type=mysql.INTEGER(),
               type_=sa.String(length=128),
               existing_nullable=False)
    op.create_index(op.f('ix_files_user_id'), 'files', ['user_id'], unique=False)
    op.drop_constraint('files_ibfk_1', 'files', type_='foreignkey')
    op.add_column('outputs', sa.Column('title', sa.String(length=100), nullable=False))
    op.alter_column('outputs', 'user_id',
               existing_type=mysql.INTEGER(),
               type_=sa.String(length=128),
               existing_nullable=False)
    op.create_index(op.f('ix_outputs_user_id'), 'outputs', ['user_id'], unique=False)
    op.drop_constraint('outputs_ibfk_1', 'outputs', type_='foreignkey')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('outputs_ibfk_1', 'outputs', 'users', ['user_id'], ['id'])
    op.drop_index(op.f('ix_outputs_user_id'), table_name='outputs')
    op.alter_column('outputs', 'user_id',
               existing_type=sa.String(length=128),
               type_=mysql.INTEGER(),
               existing_nullable=False)
    op.drop_column('outputs', 'title')
    op.create_foreign_key('files_ibfk_1', 'files', 'users', ['user_id'], ['id'])
    op.drop_index(op.f('ix_files_user_id'), table_name='files')
    op.alter_column('files', 'user_id',
               existing_type=sa.String(length=128),
               type_=mysql.INTEGER(),
               existing_nullable=False)
    op.drop_column('files', 'updated_at')
    op.drop_column('exercises', 'difficulty')
    op.drop_column('exercises', 'title')
    op.create_table('users',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('username', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=256), nullable=False),
    sa.Column('email', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=256), nullable=False),
    sa.Column('password', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=256), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_users_username', 'users', ['username'], unique=False)
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.drop_table('output_file')
    op.drop_table('exercise_file')
    op.drop_index(op.f('ix_notes_user_id'), table_name='notes')
    op.drop_index(op.f('ix_notes_title'), table_name='notes')
    op.drop_index(op.f('ix_notes_id'), table_name='notes')
    op.drop_table('notes')
    # ### end Alembic commands ###
