"""empty message

Revision ID: 8eb149ad2c24
Revises: 
Create Date: 2023-07-04 17:32:10.620897

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8eb149ad2c24'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('PDF_file',
    sa.Column('pid', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('pid')
    )
    op.create_table('User',
    sa.Column('uid', sa.Integer(), nullable=False),
    sa.Column('fname', sa.String(length=255), nullable=True),
    sa.Column('lname', sa.String(length=255), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('uid'),
    sa.UniqueConstraint('email')
    )
    op.create_table('Conversation',
    sa.Column('cid', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('pid', sa.Integer(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('question', sa.String(length=255), nullable=True),
    sa.Column('answer', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['pid'], ['PDF_file.pid'], ),
    sa.ForeignKeyConstraint(['user_id'], ['User.uid'], ),
    sa.PrimaryKeyConstraint('cid')
    )
    op.create_table('Quiz',
    sa.Column('quiz_id', sa.Integer(), nullable=False),
    sa.Column('uid', sa.Integer(), nullable=True),
    sa.Column('subject', sa.String(length=255), nullable=True),
    sa.Column('quiz_question', sa.String(length=255), nullable=True),
    sa.Column('quiz_answer', sa.String(length=255), nullable=True),
    sa.Column('opt1', sa.String(length=255), nullable=True),
    sa.Column('opt2', sa.String(length=255), nullable=True),
    sa.Column('opt3', sa.String(length=255), nullable=True),
    sa.Column('opt4', sa.String(length=255), nullable=True),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['uid'], ['User.uid'], ),
    sa.PrimaryKeyConstraint('quiz_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Quiz')
    op.drop_table('Conversation')
    op.drop_table('User')
    op.drop_table('PDF_file')
    # ### end Alembic commands ###