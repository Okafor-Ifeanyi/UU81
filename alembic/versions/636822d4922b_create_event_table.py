"""create Event table

Revision ID: 636822d4922b
Revises: 
Create Date: 2022-05-11 08:54:14.701567

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '636822d4922b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("events", sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
                    sa.Column('title', sa.String(), nullable=False))
    pass


def downgrade():
    op.drop_table("events")
    pass
