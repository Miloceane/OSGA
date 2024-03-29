"""Added password salt in Users table.

Revision ID: 26af0f10c5e1
Revises: 74e41ad351bd
Create Date: 2020-07-20 15:11:22.869339

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '26af0f10c5e1'
down_revision = '74e41ad351bd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password_salt', sa.String(length=64), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('password_salt')

    # ### end Alembic commands ###
