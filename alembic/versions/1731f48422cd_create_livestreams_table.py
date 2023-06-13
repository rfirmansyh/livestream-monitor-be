"""create livestreams table

Revision ID: 1731f48422cd
Revises: 
Create Date: 2023-05-28 18:52:25.646634

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1731f48422cd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'livestreams',
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('title', sa.String(255), nullable=True),
    sa.Column('description', sa.Text, nullable=True),
    sa.Column('thumbnails', sa.JSON, default=lambda: {}),
    sa.Column('channel_id', sa.String(255), nullable=True),
    sa.Column('tags', sa.JSON, default=lambda: {}, nullable=True),
    sa.Column('livestream_url_id', sa.String(255), nullable=True),
    sa.Column('livestream_livechat_id', sa.String(255), nullable=True),
    sa.Column('livestream_start_time', sa.DateTime, nullable=True),
    sa.Column('livestream_end_time', sa.DateTime, nullable=True),
    sa.Column('livestream_max_viewers', sa.Integer, nullable=True),
    sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now(), default=sa.func.now()),
  )


def downgrade() -> None:
  op.drop_table('livestreams')
