"""empty message

Revision ID: 3e1d0b643ea5
Revises: a984cda0cf9f
Create Date: 2022-05-23 01:19:07.931333

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3e1d0b643ea5'
down_revision = 'a984cda0cf9f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Artist', 'num_upcoming_shows',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Artist', 'num_upcoming_shows',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
