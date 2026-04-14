# backend/alembic/versions/002_add_optimizer_tables.py

"""Add optimizer tables

Revision ID: 002
Revises: 001
Create Date: 2026-03-25
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Stores cached suggestions per user + draft combo
    op.create_table(
        'optimizer_suggestions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('platforms', ARRAY(sa.String()), nullable=False),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('title_draft', sa.Text(), nullable=True),
        sa.Column('description_draft', sa.Text(), nullable=True),
        sa.Column('suggestions', JSONB, nullable=False),  # Full response cached
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_optimizer_suggestions_user_id', 'optimizer_suggestions', ['user_id'])

    # Stores user upload performance data for time optimization
    op.create_table(
        'upload_performance',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('video_id', sa.Integer(), sa.ForeignKey('videos.video_id'), nullable=True),
        sa.Column('platform', sa.String(50), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('day_of_week', sa.Integer(), nullable=False),  # 0=Mon, 6=Sun
        sa.Column('hour_of_day', sa.Integer(), nullable=False),  # 0-23
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_upload_performance_user_platform', 'upload_performance', ['user_id', 'platform'])


def downgrade():
    op.drop_table('upload_performance')
    op.drop_table('optimizer_suggestions')
