"""New migration after resetting

Revision ID: efbb39efabf2
Revises: 
Create Date: 2025-01-26 13:42:04.502886

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'efbb39efabf2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('assignment')
    op.drop_table('class_code')
    op.drop_table('student_class_codes')
    op.drop_table('student_class_code')
    op.drop_table('assignment_reminder')
    op.drop_table('classes')
    op.drop_index('email', table_name='users')
    op.drop_index('username', table_name='users')
    op.drop_table('users')
    op.drop_table('teachers')
    op.drop_index('email', table_name='students')
    op.drop_table('students')
    op.drop_table('assignments')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('assignments',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('class_code_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['class_code_id'], ['class_code.id'], name='assignments_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('students',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('first_name', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('last_name', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('email', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('dob', sa.DATE(), nullable=False),
    sa.Column('enrollment_date', mysql.TIMESTAMP(), nullable=True),
    sa.Column('status', mysql.ENUM('active', 'inactive'), nullable=True),
    sa.Column('password_hash', mysql.VARCHAR(length=128), nullable=False),
    sa.Column('class_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['class_id'], ['classes.id'], name='students_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('email', 'students', ['email'], unique=True)
    op.create_table('teachers',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('users',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('username', mysql.VARCHAR(length=150), nullable=False),
    sa.Column('email', mysql.VARCHAR(length=150), nullable=False),
    sa.Column('password_hash', mysql.VARCHAR(length=256), nullable=False),
    sa.Column('role', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('is_admin_field', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('class_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('created_by_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('creator_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['class_id'], ['classes.id'], name='users_ibfk_1'),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], name='users_ibfk_2'),
    sa.ForeignKeyConstraint(['creator_id'], ['users.id'], name='users_ibfk_3'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('username', 'users', ['username'], unique=True)
    op.create_index('email', 'users', ['email'], unique=True)
    op.create_table('classes',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('assignment_reminder',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('assignment_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('reminder_date', sa.DATE(), nullable=True),
    sa.ForeignKeyConstraint(['assignment_id'], ['assignment.id'], name='assignment_reminder_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('student_class_code',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('code', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('description', mysql.VARCHAR(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('student_class_codes',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('code', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('description', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('student_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('class_code_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('joined_at', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['class_code_id'], ['class_code.id'], name='student_class_codes_ibfk_2'),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], name='student_class_codes_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('class_code',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('code', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('description', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('creator_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('created_at', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['creator_id'], ['users.id'], name='class_code_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('assignment',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('description', mysql.TEXT(), nullable=True),
    sa.Column('due_date', sa.DATE(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
