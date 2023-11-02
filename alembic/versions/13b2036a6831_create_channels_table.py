"""create channels table

Revision ID: 13b2036a6831
Revises: 
Create Date: 2023-07-18 01:53:01.292170

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '13b2036a6831'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'channels',
    # id from youtube api
    sa.Column('id', sa.String(255), primary_key=True, unique=True),
    sa.Column('title', sa.String(255), nullable=True),
    sa.Column('description', sa.Text, nullable=True),
    sa.Column('thumbnails', sa.JSON, default=lambda: {}),
    sa.Column('subscriber_count', sa.Integer, nullable=True),
    sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now(), default=sa.func.now()),
  )


def downgrade() -> None:
  op.drop_table('channels')