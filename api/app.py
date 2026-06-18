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
    
@app.get("/run-pipeline")
def run_pipeline_endpoint():
    try:
        from pipeline.runner import run_pipeline
        run_pipeline(batch_size=10, delay_seconds=8.0)
        return {"status": "ok", "message": "Pipeline completed!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
