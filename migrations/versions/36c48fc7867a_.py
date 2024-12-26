"""empty message

Revision ID: 36c48fc7867a
Revises: 2247c695a01e
Create Date: 2024-12-26 10:47:59.739148

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '36c48fc7867a'
down_revision = '2247c695a01e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('student_class_code', schema=None) as batch_op:
        batch_op.add_column(sa.Column('code', sa.String(length=50), nullable=False))
        batch_op.add_column(sa.Column('description', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('student_class_code', schema=None) as batch_op:
        batch_op.drop_column('description')
        batch_op.drop_column('code')

    # ### end Alembic commands ###
