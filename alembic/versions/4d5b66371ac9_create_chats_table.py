"""create chats table

Revision ID: 4d5b66371ac9
Revises: e63105625244
Create Date: 2023-07-18 01:53:29.767458

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4d5b66371ac9'
down_revision = 'e63105625244'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'chats',
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    # id from youtube api
    sa.Column('livechat_id', sa.String(255), unique=True),
    sa.Column('has_display_content', sa.Boolean, default=False),
    sa.Column('display_message', sa.String(255), nullable=True),
    sa.Column('author_channel_id', sa.String(255)),
    sa.Column('author_channel_url', sa.String(255)),
    sa.Column('author_display_name', sa.String(255)),
    sa.Column('author_image_url', sa.String(255)),
    sa.Column('predicted_as', sa.String(255), nullable=True),
    sa.Column('livestream_id', sa.Integer, nullable=True),
    sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    
    sa.ForeignKeyConstraint(['livestream_id'], ['livestreams.id'], 'fk_chats_livestreams')
  )


def downgrade() -> None:
  op.drop_constraint('fk_chats_livestreams', 'chats', type_='foreignkey')
  op.drop_table('chats')
