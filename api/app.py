from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router
from api.street_vendor_routes import router as street_vendor_router

app.include_router(street_vendor_router)

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

@app.get("/init-street-vendors")
def init_street_vendors_table():
    try:
        from db.database import Base, engine
        Base.metadata.create_all(bind=engine)
        return {"status": "ok", "message": "Bảng street_vendors đã tạo!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
