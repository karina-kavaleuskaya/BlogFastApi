"""Delete notif 2

Revision ID: 3292b332c6d6
Revises: 872844bfd9aa
Create Date: 2024-07-16 16:50:12.983232

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3292b332c6d6'
down_revision: Union[str, None] = '872844bfd9aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('notification')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notification',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('post_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], name='notification_post_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='notification_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='notification_pkey')
    )
    # ### end Alembic commands ###