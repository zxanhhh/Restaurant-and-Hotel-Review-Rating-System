from functools import lru_cache
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from db.database import get_session
from db.models import AnalysisResult, Category

VALID_SENTIMENTS = {"positive", "neutral", "negative"}
CONFIDENCE_THRESHOLD = 0.15   # Bỏ qua kết quả có confidence quá thấp


@lru_cache(maxsize=32)
def get_category_id(category_name: str) -> int | None:
    """
    Tra cứu id của category theo tên
    Dùng lru_cache để tránh query DB lặp lại
    Gọi get_category_id.cache_clear() nếu cần reset (ví dụ: sau khi re-seed DB)
    """
    with get_session() as session:
        cat = session.query(Category).filter_by(name=category_name).first()
        return cat.id if cat else None


def save_analysis(review_id: int, analysis: dict) -> int:
    """
    Lưu kết quả phân tích từ Claude vào bảng analysis_results
    Dùng UPSERT (ON CONFLICT DO UPDATE) để an toàn khi pipeline chạy lại

    Returns:
        Số category đã lưu thành công
    """
    saved = 0

    with get_session() as session:
        for cat_name, result in analysis.get("categories", {}).items():
            # 1. Kiểm tra category tồn tại
            cat_id = get_category_id(cat_name)
            if cat_id is None:
                print(f"  [WARN] Category '{cat_name}' không tồn tại trong DB, skipping.")
                continue

            # 2. Bỏ qua kết quả confidence quá thấp
            confidence = float(result.get("confidence", 0.5))
            if confidence < CONFIDENCE_THRESHOLD:
                continue

            # 3. Validate và normalize sentiment
            sentiment = result.get("sentiment", "neutral")
            if sentiment not in VALID_SENTIMENTS:
                print(f"  [WARN] Invalid sentiment '{sentiment}' cho '{cat_name}', đặt về 'neutral'.")
                sentiment = "neutral"

            # 4. UPSERT vào DB
            stmt = pg_insert(AnalysisResult).values(
                review_id        = review_id,
                category_id      = cat_id,
                sentiment        = sentiment,
                strength_text    = result.get("strength"),
                weakness_text    = result.get("weakness"),
                confidence_score = confidence,
            ).on_conflict_do_update(
                index_elements = ["review_id", "category_id"],
                set_ = {
                    "sentiment":        sentiment,
                    "strength_text":    result.get("strength"),
                    "weakness_text":    result.get("weakness"),
                    "confidence_score": confidence,
                    "analyzed_at":      func.now(),
                }
            )
            session.execute(stmt)
            saved += 1

    return saved
