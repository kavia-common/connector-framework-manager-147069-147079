"""Initial migration - create all tables with constraints, indexes, and JSON/JSONB types.

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# Try to import PostgreSQL JSONB if available; fallback to JSON otherwise
try:
    from sqlalchemy.dialects.postgresql import JSONB
    JSONType = JSONB
except Exception:  # pragma: no cover
    JSONType = sa.JSON

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables with proper constraints and indexes."""
    # users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('email', sa.String(length=320), nullable=False, unique=True, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    # Index for quicker lookup by email (unique already adds index in many DBs, but explicit for clarity)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # connectors
    op.create_table(
        'connectors',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False, unique=True, index=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('config_schema', JSONType, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_connectors_key', 'connectors', ['key'], unique=True)

    # connections
    op.create_table(
        'connections',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('connector_id', sa.Integer(), nullable=False),
        sa.Column('config_data', JSONType, nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(['connector_id'], ['connectors.id'], ondelete="CASCADE"),
        sa.UniqueConstraint('user_id', 'connector_id', name='uq_connection_per_user_connector'),
    )
    op.create_index('ix_connections_user_id', 'connections', ['user_id'])
    op.create_index('ix_connections_connector_id', 'connections', ['connector_id'])
    op.create_index('ix_connections_status', 'connections', ['status'])

    # oauth_tokens
    op.create_table(
        'oauth_tokens',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('connection_id', sa.Integer(), nullable=False),
        sa.Column('access_token', sa.String(length=2048), nullable=False),
        sa.Column('refresh_token', sa.String(length=2048), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['connection_id'], ['connections.id'], ondelete="CASCADE"),
    )
    op.create_index('ix_oauth_tokens_connection_id', 'oauth_tokens', ['connection_id'])


def downgrade() -> None:
    """Drop all tables (reverse order of dependencies)."""
    op.drop_index('ix_oauth_tokens_connection_id', table_name='oauth_tokens')
    op.drop_table('oauth_tokens')

    op.drop_index('ix_connections_status', table_name='connections')
    op.drop_index('ix_connections_connector_id', table_name='connections')
    op.drop_index('ix_connections_user_id', table_name='connections')
    op.drop_table('connections')

    op.drop_index('ix_connectors_key', table_name='connectors')
    op.drop_table('connectors')

    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
