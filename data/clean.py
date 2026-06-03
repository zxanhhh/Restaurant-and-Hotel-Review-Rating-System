from sqlalchemy import func, delete
from db.database import get_session
from db.models import Review

MIN_CONTENT_LENGTH = 20


def clean_reviews():
    """
    Làm sạch bảng reviews:
    1. Xóa review quá ngắn (< 20 ký tự) - không đủ context cho AI phân tích
    2. Strip whitespace thừa ở đầu/cuối content.
    """
    with get_session() as session:
        # Bước 1: Xóa review quá ngắn
        deleted = session.execute(
            delete(Review).where(
                func.length(Review.content) < MIN_CONTENT_LENGTH
            )
        )
        n_deleted = deleted.rowcount
        print(f"Deleted {n_deleted} reviews shorter than {MIN_CONTENT_LENGTH} chars.")

        # Bước 2: chỉ update những row thực sự cần thiết
        reviews = session.query(Review).all()
        n_stripped = 0
        for r in reviews:
            cleaned = r.content.strip()
            if cleaned != r.content:
                r.content = cleaned
                n_stripped += 1

        print(f"Stripped whitespace for {n_stripped} reviews.")

    print("Cleaning done.")


if __name__ == "__main__":
    clean_reviews()
