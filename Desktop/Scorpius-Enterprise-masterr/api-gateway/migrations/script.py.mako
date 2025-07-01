from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '${up_revision}'
down_revision = ${down_revision and "'" + down_revision + "'" or 'None'}
branch_labels = ${branch_labels or 'None'}
depends_on = ${depends_on or 'None'}


def upgrade():
    pass

def downgrade():
    pass
