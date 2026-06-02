import random
from datetime import date, timedelta
from faker import Faker
from db.database import get_session
from db.models import Business, Review

fake = Faker()

BUSINESS_TYPES = ["restaurant", "hotel", "cafe"]

REVIEW_TEMPLATES = {
    "positive": [
        "Món ăn tuyệt vời, nhân viên rất thân thiện và phục vụ nhanh.",
        "Không gian đẹp, giá cả hợp lý. Chắc chắn sẽ quay lại.",
        "Phòng sạch sẽ, view đẹp, breakfast rất ngon. Highly recommend!",
        "Nhân viên nhiệt tình, đồ ăn nóng hổi và được trình bày đẹp mắt.",
        "Dịch vụ xuất sắc từ lúc check-in đến lúc check-out. Rất hài lòng.",
    ],
    "mixed": [
        "Đồ ăn ngon nhưng phải đợi hơi lâu. Nhân viên thì ổn.",
        "Giá hơi cao so với chất lượng nhưng không gian thì tốt.",
        "Service chậm nhưng bù lại món ăn rất đáng tiền.",
        "Phòng sạch nhưng tiếng ồn từ phòng bên cạnh khá lớn.",
        "Breakfast ngon, nhưng hồ bơi xuống cấp cần tu sửa.",
    ],
    "negative": [
        "Phục vụ quá chậm, gọi mãi không ai ra. Rất thất vọng.",
        "Phòng không sạch, có mùi ẩm. Không xứng với mức giá.",
        "Đồ ăn nguội, nhạt. Sẽ không quay lại.",
        "Nhân viên thô lỗ và thiếu chuyên nghiệp. Trải nghiệm tệ.",
        "Giá trên trời nhưng chất lượng rất bình thường, không đáng tiền.",
    ],
}


def generate_businesses(n: int = 10) -> list[Business]:
    businesses = []
    for _ in range(n):
        businesses.append(Business(
            name    = fake.company(),
            type    = random.choice(BUSINESS_TYPES),
            address = fake.address(),
            city    = random.choice(["Hanoi", "HCMC", "Da Nang", "Hue", "Can Tho"]),
            source  = "mock",
        ))
    return businesses


def generate_reviews(business_ids: list[int], n_per_business: int = 20) -> list[Review]:
    reviews = []
    for bid in business_ids:
        for _ in range(n_per_business):
            bucket = random.choices(
                ["positive", "mixed", "negative"],
                weights=[0.5, 0.3, 0.2]
            )[0]
            lo, hi = {"positive": (3.5, 5.0), "mixed": (2.5, 3.5), "negative": (1.0, 2.5)}[bucket]
            reviews.append(Review(
                business_id   = bid,
                reviewer_name = fake.name(),
                rating        = round(random.uniform(lo, hi), 1),
                content       = random.choice(REVIEW_TEMPLATES[bucket]),
                review_date   = fake.date_between(
                    start_date=date.today() - timedelta(days=365),
                    end_date=date.today()
                ),
                source = "mock",
            ))
    return reviews


def seed_mock_data(n_businesses: int = 10, reviews_per_business: int = 20):
    with get_session() as session:
        businesses = generate_businesses(n_businesses)
        session.add_all(businesses)
        session.flush()

        reviews = generate_reviews(
            business_ids=[b.id for b in businesses],
            n_per_business=reviews_per_business,
        )
        session.add_all(reviews)

    total = n_businesses * reviews_per_business
    print(f"Seeded {n_businesses} businesses, {total} reviews.")


if __name__ == "__main__":
    seed_mock_data()
