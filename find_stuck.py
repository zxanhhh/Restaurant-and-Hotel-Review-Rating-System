import os
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://neondb_owner:npg_9bXWyQMnBdV3@ep-damp-tooth-ao33ul6k-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require'

from db.database import get_session
from db.models import AnalysisResult, Category

STUCK_ID = 1836

with get_session() as session:
    cat = session.query(Category).first()
    placeholder = AnalysisResult(
        review_id=STUCK_ID,
        category_id=cat.id,
        sentiment="neutral",
        confidence_score=0.0,
    )
    session.add(placeholder)
    session.commit()
    print(f"Đã skip review_id={STUCK_ID}")