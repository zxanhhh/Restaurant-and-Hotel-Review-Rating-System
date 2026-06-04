from dotenv import load_dotenv
load_dotenv()

from db.database import init_db
from data.generate_mock import seed_mock_data
from data.clean import clean_reviews
from pipeline.runner import run_pipeline


def main():
    print("=== 1. Khởi tạo database ===")
    init_db()

    print("\n=== 2. Seed mock data ===")
    seed_mock_data(n_businesses=5, reviews_per_business=10)

    print("\n=== 3. Làm sạch dữ liệu ===")
    clean_reviews()

    print("\n=== 4. Dry run pipeline (kiểm tra prompt) ===")
    run_pipeline(batch_size=2, dry_run=True)

    print("\n=== 5. Chạy pipeline thật ===")
    run_pipeline(batch_size=50, delay_seconds=0.5)


if __name__ == "__main__":
    main()
