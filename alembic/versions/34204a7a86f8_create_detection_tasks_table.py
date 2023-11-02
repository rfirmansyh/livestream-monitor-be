"""create detection_tasks table

Revision ID: 34204a7a86f8
Revises: 4d5b66371ac9
Create Date: 2023-07-18 01:53:36.700113

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '34204a7a86f8'
down_revision = '4d5b66371ac9'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'detection_tasks',
    sa.Column('id', sa.String(255), primary_key=True),
    # task_id from celery
    sa.Column('livestream_a_id', sa.Integer),
    sa.Column('livestream_a_url_id', sa.String(255)),
    sa.Column('livestream_b_id', sa.Integer),
    sa.Column('livestream_b_url_id', sa.String(255)),
    sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    sa.Column('ended_at', sa.DateTime, nullable=True),
    
    sa.ForeignKeyConstraint(['livestream_a_id'], ['livestreams.id'], 'fk_detection_tasks_livestream_a'),
    sa.ForeignKeyConstraint(['livestream_b_id'], ['livestreams.id'], 'fk_detection_tasks_livestream_b')
  )


def downgrade() -> None:
  op.drop_constraint('fk_detection_tasks_livestream_a', 'detection_tasks', type_='foreignkey')
  op.drop_constraint('fk_detection_tasks_livestream_b', 'detection_tasks', type_='foreignkey')
  op.drop_table('detection_tasks')
