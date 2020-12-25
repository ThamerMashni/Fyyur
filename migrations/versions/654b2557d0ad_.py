"""empty message

Revision ID: 654b2557d0ad
Revises: 8c2aab1a85c4
Create Date: 2020-12-25 15:37:18.995337

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '654b2557d0ad'
down_revision = '8c2aab1a85c4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Artist', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('Venue', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Venue', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('Artist', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###
