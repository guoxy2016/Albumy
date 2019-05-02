"""user add pub_col

Revision ID: a0e8f04ab8c9
Revises: 4eb71a1fcf3b
Create Date: 2019-05-02 16:11:36.696742

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a0e8f04ab8c9'
down_revision = '4eb71a1fcf3b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user') as batch_op:
        batch_op.add_column(sa.Column('public_collections', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user') as batch_op:
        batch_op.drop_column('public_collections')
    # ### end Alembic commands ###
