import time
from sqlalchemy import text
from db.database import get_session
from db.models import Review, AnalysisResult
from .gemini_client import analyze_review
from .store import save_analysis
from .prompt import build_user_prompt


def get_unanalyzed_reviews(batch_size: int = 50) -> list[dict]:
    """
    Lấy các review chưa có bất kỳ analysis_result nào
    Trả về list[dict] thay vì ORM objects để tránh DetachedInstanceError
    """
    with get_session() as session:
        analyzed_ids = (
            session.query(AnalysisResult.review_id)
            .distinct()
            .subquery()
        )
        rows = (
            session.query(Review.id, Review.content, Review.business_id)
            .filter(Review.id.notin_(analyzed_ids))
            .limit(batch_size)
            .all()
        )
        return [
            {"id": r.id, "content": r.content, "business_id": r.business_id}
            for r in rows
        ]


def _refresh_insights(business_ids: list[int]):
    """Gọi stored function refresh_insights() chỉ cho các business có data mới."""
    unique_ids = set(business_ids)
    with get_session() as session:
        for bid in unique_ids:
            session.execute(text("SELECT refresh_insights(:bid)"), {"bid": bid})
    print(f"Refreshed insights cho {len(unique_ids)} businesses.")


def run_pipeline(
    batch_size: int     = 50,
    delay_seconds: float = 0.5,
    dry_run: bool       = False,
):
    """
    Orchestrate toàn bộ pipeline phân tích review

    Args:
        batch_size:     Số review xử lý mỗi lần chạy
        delay_seconds:  Delay giữa các API call để tránh rate limit
        dry_run:        Nếu True, chỉ in prompt ra màn hình, không gọi API
    """
    reviews = get_unanalyzed_reviews(batch_size)

    if not reviews:
        print("Không còn review nào chưa phân tích.")
        return

    print(f"Bắt đầu phân tích {len(reviews)} reviews...")
    success, failed = 0, 0
    business_ids_processed: list[int] = []

    for i, review in enumerate(reviews, 1):
        print(f"\n[{i}/{len(reviews)}] review_id={review['id']}", end=" ")

        if dry_run:
            print("(dry run)")
            print("--- USER PROMPT ---")
            print(build_user_prompt(review["content"]))
            print("-------------------")
            continue

        result = analyze_review(review["content"])

        if result is None:
            print("=> FAILED")
            failed += 1
            continue

        n_saved = save_analysis(review["id"], result)
        business_ids_processed.append(review["business_id"])
        print(f"=> OK ({n_saved} categories saved)")
        success += 1

        time.sleep(delay_seconds)

    if not dry_run:
        print(f"\nHoàn tất: {success} thành công, {failed} thất bại.")
        if success > 0:
            _refresh_insights(business_ids_processed)
