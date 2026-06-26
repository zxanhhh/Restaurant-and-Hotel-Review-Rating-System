import os
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://neondb_owner:npg_9bXWyQMnBdV3@ep-damp-tooth-ao33ul6k-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require'
os.environ['GOOGLE_API_KEY'] = 'AQ.Ab8RN6Ix31_bEvUkMreYM8bWiVtbuycPz1Um7KEEpIJ4kBwPdA'

from pipeline.runner import run_pipeline
run_pipeline(batch_size=10, delay_seconds=5.0)
