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
        import time
        from pipeline.runner import get_unanalyzed_reviews, _refresh_insights
        from pipeline.gemini_client import analyze_review
        from pipeline.store import save_analysis

        total_success = 0
        total_failed  = 0
        business_ids  = []

        while True:
            reviews = get_unanalyzed_reviews(batch_size=10)
            if not reviews:
                break

            for review in reviews:
                while True:
                    result = analyze_review(review["content"])
                    if result is not None:
                        save_analysis(review["id"], result)
                        business_ids.append(review["business_id"])
                        total_success += 1
                        break
                    else:
                        time.sleep(65)

                time.sleep(5)

        if business_ids:
            _refresh_insights(business_ids)

        return {
            "status":  "ok",
            "success": total_success,
            "failed":  total_failed,
            "message": f"Analyzed {total_success} reviews!"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
