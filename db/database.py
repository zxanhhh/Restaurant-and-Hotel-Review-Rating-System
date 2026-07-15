import os
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .models import Base
from db.street_vendor_models import StreetVendor

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/review_db")

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }
)
SessionLocal = sessionmaker(bind=engine)


@contextmanager
def get_session():
    """Context manager an toàn: auto commit, rollback khi lỗi, luôn close."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


CATEGORY_SEED = [
    ("Food",        "Chất lượng món ăn, hương vị, định lượng"),
    ("Service",     "Thái độ nhân viên, sự chuyên nghiệp"),
    ("Wait Time",   "Thời gian chờ đợi, tốc độ phục vụ"),
    ("Ambiance",    "Không gian, âm nhạc, trang trí"),
    ("Price",       "Giá cả, tính hợp lý của chi phí"),
    ("Cleanliness", "Vệ sinh nhà hàng, bàn ghế, nhà vệ sinh"),
]


def init_db():
    Base.metadata.create_all(engine)
    _seed_categories()
    _create_indexes_and_triggers()
    print("Database initialized successfully.")


def _seed_categories():
    from .models import Category
    with get_session() as session:
        for name, desc in CATEGORY_SEED:
            exists = session.query(Category).filter_by(name=name).first()
            if not exists:
                session.add(Category(name=name, description=desc))


def _create_indexes_and_triggers():
    ddl_statements = [
        # --- Index ---
        "CREATE INDEX IF NOT EXISTS idx_reviews_business   ON reviews(business_id)",
        "CREATE INDEX IF NOT EXISTS idx_reviews_date       ON reviews(review_date)",
        "CREATE INDEX IF NOT EXISTS idx_analysis_review    ON analysis_results(review_id)",
        "CREATE INDEX IF NOT EXISTS idx_analysis_category  ON analysis_results(category_id)",
        "CREATE INDEX IF NOT EXISTS idx_analysis_sentiment ON analysis_results(sentiment)",
        "CREATE INDEX IF NOT EXISTS idx_insights_business  ON insights_summary(business_id)",
        "CREATE INDEX IF NOT EXISTS idx_insights_category  ON insights_summary(category_id)",

        # --- View: avg_rating động ---
        """
        CREATE OR REPLACE VIEW business_avg_rating AS
        SELECT
            b.id   AS business_id,
            b.name AS name,
            ROUND(AVG(r.rating)::NUMERIC, 2) AS avg_rating,
            COUNT(r.id) AS total_reviews
        FROM businesses b
        LEFT JOIN reviews r ON r.business_id = b.id
        GROUP BY b.id, b.name
        """,

        # --- Trigger: cập nhật updated_at cho insights_summary ---
        """
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
        """,
        """
        DROP TRIGGER IF EXISTS trg_insights_updated_at ON insights_summary
        """,
        """
        CREATE TRIGGER trg_insights_updated_at
        BEFORE UPDATE ON insights_summary
        FOR EACH ROW EXECUTE FUNCTION set_updated_at()
        """,

        # --- Stored function: refresh insights cho một business ---
        """
        CREATE OR REPLACE FUNCTION refresh_insights(p_business_id INT)
        RETURNS VOID AS $$
        BEGIN
            INSERT INTO insights_summary (
                business_id, category_id, total_reviews,
                pct_positive, pct_neutral, pct_negative, updated_at
            )
            SELECT
                r.business_id,
                ar.category_id,
                COUNT(*) AS total_reviews,
                ROUND(100.0 * SUM(CASE WHEN ar.sentiment = 'positive' THEN 1 ELSE 0 END) / COUNT(*), 2),
                ROUND(100.0 * SUM(CASE WHEN ar.sentiment = 'neutral'  THEN 1 ELSE 0 END) / COUNT(*), 2),
                ROUND(100.0 * SUM(CASE WHEN ar.sentiment = 'negative' THEN 1 ELSE 0 END) / COUNT(*), 2),
                NOW()
            FROM analysis_results ar
            JOIN reviews r ON r.id = ar.review_id
            WHERE r.business_id = p_business_id
            GROUP BY r.business_id, ar.category_id
            ON CONFLICT (business_id, category_id)
            DO UPDATE SET
                total_reviews = EXCLUDED.total_reviews,
                pct_positive  = EXCLUDED.pct_positive,
                pct_neutral   = EXCLUDED.pct_neutral,
                pct_negative  = EXCLUDED.pct_negative,
                updated_at    = NOW();
        END;
        $$ LANGUAGE plpgsql
        """,
    ]

    with engine.connect() as conn:
        for stmt in ddl_statements:
            conn.execute(text(stmt))
        conn.commit()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
