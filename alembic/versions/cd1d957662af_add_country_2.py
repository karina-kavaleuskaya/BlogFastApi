"""Add country 2

Revision ID: cd1d957662af
Revises: bd5451563849
Create Date: 2024-06-30 20:18:20.646622

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cd1d957662af'
down_revision: Union[str, None] = 'bd5451563849'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('country',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sex',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('user', sa.Column('sex_id', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('country_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'user', 'sex', ['sex_id'], ['id'])
    op.create_foreign_key(None, 'user', 'country', ['country_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_column('user', 'country_id')
    op.drop_column('user', 'sex_id')
    op.drop_table('sex')
    op.drop_table('country')
    # ### end Alembic commands ###
