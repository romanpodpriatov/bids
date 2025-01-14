"""Initial migration

Revision ID: f0ced61883f3
Revises: 
Create Date: 2024-09-22 03:36:18.671292

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f0ced61883f3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('auctions', sa.Column('image_filename', sa.String(), nullable=False, server_default='default.jpg'))
    op.drop_column('auctions', 'image_url')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('auctions', sa.Column('image_url', sa.VARCHAR(), nullable=False))
    op.drop_column('auctions', 'image_filename')
    # ### end Alembic commands ###
