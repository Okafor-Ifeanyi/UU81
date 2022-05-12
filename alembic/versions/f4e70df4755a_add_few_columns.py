"""add few columns

Revision ID: f4e70df4755a
Revises: 1cbeb5c84320
Create Date: 2022-05-12 11:27:10.793744

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f4e70df4755a'
down_revision = '1cbeb5c84320'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('events', sa.Column(
        'content', sa.String(), nullable=False))
    op.add_column('events', sa.Column(
        'space_available', sa.Integer(), nullable=False))
    op.add_column('events', sa.Column(
        'cost', sa.Integer(), nullable=False))
    op.add_column('events', sa.Column(
        'status', sa.Boolean(), nullable=False, server_default='True'))
    op.add_column('events', sa.Column(
        'start_date', sa.TIMESTAMP(timezone=True)))
    op.add_column('events', sa.Column(
        'end_date', sa.TIMESTAMP(timezone=True)))
    op.add_column('events', sa.Column(
        'created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default= sa.text('now()') ))
    pass

def downgrade():
    op.drop_column('events', 'content')
    op.drop_column('events', 'space_available')
    op.drop_column('events', 'cost')
    op.drop_column('events', 'status')
    op.drop_column('events', 'start_date')
    op.drop_column('events', 'end_date')
    op.drop_column('events', 'created_at')
    pass
