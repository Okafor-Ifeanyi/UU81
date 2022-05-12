"""add User table

Revision ID: 4602e44ce5db
Revises: 3d08ad5a415e
Create Date: 2022-05-12 11:00:34.312904

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4602e44ce5db'
down_revision = '3d08ad5a415e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users', 
                sa.Column('id', sa.Integer(), nullable=False),
                sa.Column('email', sa.String(), nullable=False),
                sa.Column('password', sa.String(), nullable=False),
                sa.Column('created_at', sa.TIMESTAMP(timezone=True),
                            server_default=sa.text('now()') , nullable=False),
                sa.Column('phone_numer', sa.Integer(), nullable=False),
                sa.Column('admin', sa.Boolean(), server_default='False', nullable=False),
                sa.Column('is_host', sa.Boolean(), server_default='False', nullable=False),
                sa.PrimaryKeyConstraint('id'),
                sa.UniqueConstraint('email')
                )
    pass


def downgrade():
    op.drop_table("users")
    pass
