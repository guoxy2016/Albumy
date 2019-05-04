"""user add active block

Revision ID: 9daa3e9d32c2
Revises: a0e8f04ab8c9
Create Date: 2019-05-04 21:53:59.468500

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9daa3e9d32c2'
down_revision = 'a0e8f04ab8c9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user') as bathc_op:
        bathc_op.add_column(sa.Column('active', sa.Boolean(), nullable=True))
        bathc_op.add_column(sa.Column('locked', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user') as batch_op:
        batch_op.drop_column('locked')
        batch_op.drop_column('active')
    # ### end Alembic commands ###