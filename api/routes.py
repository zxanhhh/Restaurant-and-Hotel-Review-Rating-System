from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud
from .deps import get_db
from .schemas import (
    BusinessOut, BusinessInsightsOut,
    CategoryInsight, ReviewOut, SummaryOut,
)

router = APIRouter()


@router.get("/businesses", response_model=list[BusinessOut])
def list_businesses(db: Session = Depends(get_db)):
    return crud.get_all_businesses(db)


@router.get("/businesses/{business_id}", response_model=BusinessOut)
def get_business(business_id: int, db: Session = Depends(get_db)):
    biz = crud.get_business_by_id(db, business_id)
    if biz is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return biz


@router.get("/businesses/{business_id}/insights", response_model=BusinessInsightsOut)
def get_business_insights(business_id: int, db: Session = Depends(get_db)):
    biz = crud.get_business_by_id(db, business_id)
    if biz is None:
        raise HTTPException(status_code=404, detail="Business not found")

    rows = crud.get_insights_for_business(db, business_id)
    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Chưa có dữ liệu phân tích cho business này. Hãy chạy pipeline trước."
        )

    return BusinessInsightsOut(
        business_id   = business_id,
        business_name = biz.name,
        categories    = [CategoryInsight(**row) for row in rows],
    )


@router.get("/businesses/{business_id}/reviews", response_model=list[ReviewOut])
def get_business_reviews(
    business_id: int,
    limit:  int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    biz = crud.get_business_by_id(db, business_id)
    if biz is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return crud.get_reviews_for_business(db, business_id, limit=limit, offset=offset)


@router.get("/summary", response_model=SummaryOut)
def get_summary(db: Session = Depends(get_db)):
    return crud.get_system_summary(db)
