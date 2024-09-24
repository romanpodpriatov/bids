"""Add additional fields to User

Revision ID: cb0afc9acbff
Revises: 2d7d4bd68a40
Create Date: 2024-09-23 19:53:21.406595

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cb0afc9acbff'
down_revision = '2d7d4bd68a40'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('photo_url', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('photo_url')

    # ### end Alembic commands ###
