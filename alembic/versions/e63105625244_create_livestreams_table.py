"""create livestreams table

Revision ID: e63105625244
Revises: 13b2036a6831
Create Date: 2023-07-18 01:53:24.007558

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e63105625244'
down_revision = '13b2036a6831'
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
    
    sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], 'fk_livestreams_channels')
  )


def downgrade() -> None:
  op.drop_constraint('fk_livestreams_channels', 'livestreams', type_='foreignkey')
  op.drop_table('livestreams')
