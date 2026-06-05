from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, distinct
from db.models import Business, Review, AnalysisResult, InsightsSummary, Category


def get_all_businesses(db: Session) -> list[Business]:
    return db.query(Business).order_by(Business.name).all()


def get_business_by_id(db: Session, business_id: int) -> Business | None:
    return db.query(Business).filter(Business.id == business_id).first()


def get_insights_for_business(db: Session, business_id: int) -> list[dict]:
    rows = (
        db.query(
            Category.name.label("category"),
            InsightsSummary.total_reviews,
            InsightsSummary.pct_positive,
            InsightsSummary.pct_neutral,
            InsightsSummary.pct_negative,
            InsightsSummary.top_strengths,
            InsightsSummary.top_weaknesses,
        )
        .join(Category, InsightsSummary.category_id == Category.id)
        .filter(InsightsSummary.business_id == business_id)
        .order_by(InsightsSummary.total_reviews.desc())
        .all()
    )
    return [row._asdict() for row in rows]


def get_reviews_for_business(
    db: Session,
    business_id: int,
    limit: int = 20,
    offset: int = 0,
) -> list[dict]:
    """
    Eager load analysis_results + category trong cùng một query
    bằng joinedload để tránh DetachedInstanceError và N+1 query problem.
    """
    reviews = (
        db.query(Review)
        .options(
            joinedload(Review.analysis_results)
            .joinedload(AnalysisResult.category)
        )
        .filter(Review.business_id == business_id)
        .order_by(Review.review_date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    result = []
    for r in reviews:
        sentiments = {
            ar.category.name: ar.sentiment
            for ar in r.analysis_results
        }
        result.append({
            "review_id":     r.id,
            "reviewer_name": r.reviewer_name,
            "rating":        float(r.rating) if r.rating else None,
            "content":       r.content,
            "review_date":   r.review_date,
            "sentiments":    sentiments,
        })
    return result


def get_system_summary(db: Session) -> dict:
    total_businesses = db.query(func.count(Business.id)).scalar()
    total_reviews    = db.query(func.count(Review.id)).scalar()
    total_analyzed   = db.query(func.count(distinct(AnalysisResult.review_id))).scalar()

    sentiment_counts = (
        db.query(
            AnalysisResult.sentiment,
            func.count(AnalysisResult.id).label("cnt")
        )
        .group_by(AnalysisResult.sentiment)
        .all()
    )

    counts = {row.sentiment: row.cnt for row in sentiment_counts}
    total  = sum(counts.values()) or 1   # Guard chống chia 0

    return {
        "total_businesses": total_businesses,
        "total_reviews":    total_reviews,
        "total_analyzed":   total_analyzed,
        "overall_positive": round(counts.get("positive", 0) / total * 100, 2),
        "overall_neutral":  round(counts.get("neutral",  0) / total * 100, 2),
        "overall_negative": round(counts.get("negative", 0) / total * 100, 2),
    }
