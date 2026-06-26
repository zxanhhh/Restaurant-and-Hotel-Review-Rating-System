import os
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://neondb_owner:npg_9bXWyQMnBdV3@ep-damp-tooth-ao33ul6k-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require'

from db.database import get_session
from db.models import Business
from sqlalchemy import delete

with get_session() as session:
    deleted = session.execute(delete(Business).where(Business.source == 'mock'))
    print(f'Deleted {deleted.rowcount} mock businesses')
