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

@app.get("/reset-db")
def reset_database():
    """Endpoint tạm — xóa toàn bộ data để load lại từ Yelp."""
    try:
        from sqlalchemy import delete, text
        from db.database import get_session
        from db.models import Business
        with get_session() as session:
            # Xóa business sẽ cascade xóa reviews, analysis_results, insights
            session.execute(delete(Business))
        return {"status": "ok", "message": "Đã xóa toàn bộ data!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
