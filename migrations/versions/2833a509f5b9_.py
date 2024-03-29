"""empty message

Revision ID: 2833a509f5b9
Revises: a29c6597c60a
Create Date: 2024-02-12 22:33:35.264534

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2833a509f5b9'
down_revision = 'a29c6597c60a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('shows', 'upcoming')
    op.drop_column('shows', 'past')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows', sa.Column('past', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('shows', sa.Column('upcoming', sa.BOOLEAN(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
