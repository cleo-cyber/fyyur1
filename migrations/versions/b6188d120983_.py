"""empty message

Revision ID: b6188d120983
Revises: 57165dc16362
Create Date: 2022-05-27 23:57:58.978218

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b6188d120983'
down_revision = '57165dc16362'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('created_date', sa.DateTime(), nullable=True))
    op.drop_column('Artist', 'create_date')
    op.add_column('Venue', sa.Column('created_date', sa.DateTime(), nullable=True))
    op.drop_column('Venue', 'create_date')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('create_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('Venue', 'created_date')
    op.add_column('Artist', sa.Column('create_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('Artist', 'created_date')
    # ### end Alembic commands ###
