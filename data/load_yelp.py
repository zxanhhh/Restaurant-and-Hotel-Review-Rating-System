import json
from datetime import datetime
from db.database import get_session
from db.models import Business, Review
from dotenv import load_dotenv
load_dotenv()

YELP_BUSINESS_PATH = r"D:\D\Yelp-JSON\Yelp JSON\yelp_dataset\yelp_academic_dataset_business.json"
YELP_REVIEW_PATH   = r"D:\D\Yelp-JSON\Yelp JSON\yelp_dataset\yelp_academic_dataset_review.json"

TARGET_CATEGORIES = {"Restaurants", "Hotels", "Cafes"}


def load_yelp_businesses(limit: int = 500) -> dict[str, int]:
    """
    Đọc businesses từ Yelp, lọc chỉ lấy restaurant/hotel/cafe.
    Trả về mapping {yelp_business_id: db_id}.
    """
    yelp_to_db_id: dict[str, int] = {}

    with get_session() as session:
        count = 0
        with open(YELP_BUSINESS_PATH, encoding="utf-8") as f:
            for line in f:
                if count >= limit:
                    break
                raw = json.loads(line)

                # Tránh NoneType khi categories là null
                raw_cats = raw.get("categories") or ""
                cats = set(raw_cats.split(", "))
                if not cats & TARGET_CATEGORIES:
                    continue 

                if "Hotels" in cats:
                    btype = "hotel"
                elif "Cafes" in cats:
                    btype = "cafe"
                else:
                    btype = "restaurant"

                b = Business(
                    name    = raw["name"],
                    type    = btype,
                    address = raw.get("address", ""),
                    city    = raw.get("city", ""),
                    source  = "yelp",
                )
                session.add(b)
                session.flush()
                yelp_to_db_id[raw["business_id"]] = b.id
                count += 1

    print(f"Loaded {len(yelp_to_db_id)} businesses from Yelp.")
    return yelp_to_db_id


def load_yelp_reviews(
    yelp_to_db_id: dict[str, int],
    reviews_per_business: int = 30,
    batch_size: int = 500,
):
    """
    Đọc streaming file review, chỉ lấy review thuộc businesses đã load
    """
    business_review_count: dict[int, int] = {}
    batch: list[Review] = []
    total = 0

    with get_session() as session:
        with open(YELP_REVIEW_PATH, encoding="utf-8") as f:
            for line in f:
                raw    = json.loads(line)
                yelp_bid = raw.get("business_id")

                if yelp_bid not in yelp_to_db_id:
                    continue

                db_bid = yelp_to_db_id[yelp_bid]
                if business_review_count.get(db_bid, 0) >= reviews_per_business:
                    continue

                batch.append(Review(
                    business_id   = db_bid,
                    reviewer_name = None, 
                    rating        = float(raw["stars"]),
                    content       = raw["text"],
                    review_date   = datetime.strptime(raw["date"], "%Y-%m-%d %H:%M:%S").date(),
                    source        = "yelp",
                ))
                business_review_count[db_bid] = business_review_count.get(db_bid, 0) + 1
                total += 1

                if len(batch) >= batch_size:
                    session.add_all(batch)
                    session.flush()
                    batch.clear()
                    print(f"  Inserted {total} reviews so far...")

        if batch:
            session.add_all(batch)

    print(f"Done. Total reviews loaded: {total}")


if __name__ == "__main__":
    mapping = load_yelp_businesses(limit=100)
    load_yelp_reviews(mapping, reviews_per_business=20)
