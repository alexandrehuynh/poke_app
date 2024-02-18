"""Replace description with moves in Pokemon model

Revision ID: d5aa1ce1b945
Revises: 7367590e6d19
Create Date: 2024-02-17 22:22:56.365030

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd5aa1ce1b945'
down_revision = '7367590e6d19'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('pokemon', schema=None) as batch_op:
        batch_op.add_column(sa.Column('moves', sa.String(length=255), nullable=True))
        batch_op.drop_column('description')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('pokemon', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.VARCHAR(length=200), autoincrement=False, nullable=True))
        batch_op.drop_column('moves')

    # ### end Alembic commands ###
