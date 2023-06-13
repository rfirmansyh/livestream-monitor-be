"""create detection_tasks table

Revision ID: 5ab59a8dfef5
Revises: 3101f023499f
Create Date: 2023-05-28 18:52:59.138754

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5ab59a8dfef5'
down_revision = '3101f023499f'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'detection_tasks',
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
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
