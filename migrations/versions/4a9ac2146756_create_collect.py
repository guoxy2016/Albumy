"""create Collect

Revision ID: 4a9ac2146756
Revises: e75fd97a2606
Create Date: 2019-04-25 18:10:58.036796

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '4a9ac2146756'
down_revision = 'e75fd97a2606'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('collect',
                    sa.Column('collector_id', sa.Integer(), nullable=False),
                    sa.Column('collected_id', sa.Integer(), nullable=False),
                    sa.Column('timestamp', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['collected_id'], ['photo.id'], name=op.f('fk_collect_collected_id_photo')),
                    sa.ForeignKeyConstraint(['collector_id'], ['user.id'], name=op.f('fk_collect_collector_id_user')),
                    sa.PrimaryKeyConstraint('collector_id', 'collected_id')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('collect')
    # ### end Alembic commands ###
