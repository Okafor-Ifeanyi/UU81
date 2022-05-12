"""Complete post table

Revision ID: 1cbeb5c84320
Revises: 4602e44ce5db
Create Date: 2022-05-12 11:19:11.782134

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1cbeb5c84320'
down_revision = '4602e44ce5db'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("events", sa.Column('owner_id', sa.Integer(), nullable=False))
    op.create_foreign_key('event_users_fk', source_table="events", referent_table="users",
    local_cols=[
        'owner_id'], remote_cols=['id'], ondelete="CASCADE")
    pass


def downgrade():
    op.drop_constraint("event_users_fk", table_name="events")
    op.drop_column("events", "owner_id")
    pass
