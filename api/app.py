from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router

app = FastAPI(
    title       = "Review Rating System API",
    description = "API phân tích sentiment review nhà hàng và khách sạn",
    version     = "1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/init-db")
def initialize_database():
    try:
        from db.database import init_db
        from data.generate_mock import seed_mock_data
        init_db()
        seed_mock_data(n_businesses=10, reviews_per_business=20)
        return {"status": "ok", "message": "Database initialized and seeded successfully!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
