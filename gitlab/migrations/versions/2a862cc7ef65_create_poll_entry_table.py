"""create poll_entry table

Revision ID: 2a862cc7ef65
Revises: 
Create Date: 2023-12-07 19:34:38.211797

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a862cc7ef65'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('poll_entry',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('base_url', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('health_check_passed', sa.Boolean(), nullable=False),
    sa.Column('instance_version', sa.String(), nullable=False),
    sa.Column('readiness_check_passed', sa.Boolean(), nullable=False),
    sa.Column('error_message', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('poll_entry')
    # ### end Alembic commands ###
