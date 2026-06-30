"""Инициализация таблиц

Revision ID: 001
Revises: 
Create Date: 2026-06-29
"""

from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Создание таблиц"""
    
    op.create_table(
        'stock_events',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('sku', sa.String(50), nullable=False),
        sa.Column('qty', sa.Integer, nullable=False),
        sa.Column('warehouse', sa.String(50), nullable=False),
        sa.Column('event', sa.String(20), nullable=False),
        sa.Column('event_time', sa.DateTime, server_default=sa.func.now()),
    )
    
    op.create_table(
        'stock_agg',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('sku', sa.String(50), nullable=False),
        sa.Column('warehouse', sa.String(50), nullable=False),
        sa.Column('total_qty', sa.Integer, nullable=False, server_default='0'),
        sa.Column('updated_time', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

def downgrade() -> None:
    """Удаление таблиц"""
    op.drop_table('stock_agg')
    op.drop_table('stock_events')