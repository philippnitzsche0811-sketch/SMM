# backend/alembic/versions/003_fix_optimizer_tables.py

"""Fix optimizer tables – use String user_id matching users.id

Revision ID: 003
Revises: 002
Create Date: 2026-04-28
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Drop old tables (migration 002 used Integer user_id which doesn't match users.id String)
    op.execute("DROP TABLE IF EXISTS upload_performance CASCADE")
    op.execute("DROP TABLE IF EXISTS optimizer_suggestions CASCADE")

    op.create_table(
        'optimizer_suggestions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('platforms', ARRAY(sa.String()), nullable=False),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('title_draft', sa.Text(), nullable=True),
        sa.Column('description_draft', sa.Text(), nullable=True),
        sa.Column('suggestions', JSONB, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_optimizer_suggestions_user_id', 'optimizer_suggestions', ['user_id'])

    op.create_table(
        'upload_performance',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('platform', sa.String(50), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('day_of_week', sa.Integer(), nullable=False),
        sa.Column('hour_of_day', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_upload_performance_user_platform', 'upload_performance', ['user_id', 'platform'])


def downgrade():
    op.drop_table('upload_performance')
    op.drop_table('optimizer_suggestions')
