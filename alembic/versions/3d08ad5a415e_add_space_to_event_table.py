"""add space to event table

Revision ID: 3d08ad5a415e
Revises: 636822d4922b
Create Date: 2022-05-12 10:50:26.439348

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d08ad5a415e'
down_revision = '636822d4922b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("events", sa.Column("space_allowed",sa.Integer(), nullable=False))
    pass


def downgrade():
    op.drop_column("events", "space_allowed")
    pass
