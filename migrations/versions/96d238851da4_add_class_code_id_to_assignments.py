"""Add class_code_id to assignments

Revision ID: 96d238851da4
Revises: 36c48fc7867a
Create Date: 2024-12-27 08:25:42.263145

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '96d238851da4'
down_revision = '36c48fc7867a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('assignment_reminder')
    with op.batch_alter_table('assignments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('class_code_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'class_code', ['class_code_id'], ['id'])

    with op.batch_alter_table('student_class_code', schema=None) as batch_op:
        batch_op.alter_column('code',
               existing_type=mysql.VARCHAR(length=50),
               type_=sa.String(length=255),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('student_class_code', schema=None) as batch_op:
        batch_op.alter_column('code',
               existing_type=sa.String(length=255),
               type_=mysql.VARCHAR(length=50),
               existing_nullable=False)

    with op.batch_alter_table('assignments', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('class_code_id')

    op.create_table('assignment_reminder',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('title', mysql.VARCHAR(length=120), nullable=False),
    sa.Column('due_date', mysql.DATETIME(), nullable=False),
    sa.Column('details', mysql.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
