"""create follow

Revision ID: cc1a3828f629
Revises: 4a9ac2146756
Create Date: 2019-04-27 17:59:55.360930

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'cc1a3828f629'
down_revision = '4a9ac2146756'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('follow',
                    sa.Column('follower_id', sa.Integer(), nullable=False),
                    sa.Column('followed_id', sa.Integer(), nullable=False),
                    sa.Column('timestamp', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], name=op.f('fk_follow_followed_id_user')),
                    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], name=op.f('fk_follow_follower_id_user')),
                    sa.PrimaryKeyConstraint('follower_id', 'followed_id')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('follow')
    # ### end Alembic commands ###