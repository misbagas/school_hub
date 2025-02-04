"""Add file_url to Message model

Revision ID: 87be7d111eee
Revises: 37ede85a2fa3
Create Date: 2025-02-04 17:13:35.465603

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '87be7d111eee'
down_revision = '37ede85a2fa3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.add_column(sa.Column('file_url', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.drop_column('file_url')

    # ### end Alembic commands ###
