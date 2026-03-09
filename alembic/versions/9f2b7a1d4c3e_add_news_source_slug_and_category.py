"""add news source slug and category

Revision ID: 9f2b7a1d4c3e
Revises: 8d4f6c1a2b9e
Create Date: 2026-03-09 13:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '9f2b7a1d4c3e'
down_revision: Union[str, Sequence[str], None] = '8d4f6c1a2b9e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('news', sa.Column('source_slug', sa.String(length=200), nullable=True))
    op.add_column('news', sa.Column('category', sa.String(length=120), nullable=True))
    op.create_index(op.f('ix_news_source_slug'), 'news', ['source_slug'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_news_source_slug'), table_name='news')
    op.drop_column('news', 'category')
    op.drop_column('news', 'source_slug')
