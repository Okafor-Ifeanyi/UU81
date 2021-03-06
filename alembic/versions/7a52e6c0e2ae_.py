"""empty message

Revision ID: 7a52e6c0e2ae
Revises: e6700e527719
Create Date: 2022-06-11 10:56:39.505298

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '7a52e6c0e2ae'
down_revision = 'e6700e527719'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('events', sa.Column('image_url', sqlalchemy_utils.types.url.URLType(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('events', 'image_url')
    # ### end Alembic commands ###
