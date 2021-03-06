"""empty message

Revision ID: 8c2aab1a85c4
Revises: bfcb016f603a
Create Date: 2020-12-25 13:55:50.873662

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c2aab1a85c4'
down_revision = 'bfcb016f603a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Show', 'venue_name')
    op.drop_column('Show', 'artist_name')
    op.drop_column('Show', 'artist_image_link')
    op.drop_column('Show', 'venue_image_link')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('venue_image_link', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    op.add_column('Show', sa.Column('artist_image_link', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    op.add_column('Show', sa.Column('artist_name', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('Show', sa.Column('venue_name', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
