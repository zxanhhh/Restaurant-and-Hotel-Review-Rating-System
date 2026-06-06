from pydantic import BaseModel, ConfigDict
from datetime import date


class BusinessOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:     int
    name:   str
    type:   str
    city:   str | None
    source: str | None


class CategoryInsight(BaseModel):
    category:       str
    total_reviews:  int
    pct_positive:   float
    pct_neutral:    float
    pct_negative:   float
    top_strengths:  list[str] | None
    top_weaknesses: list[str] | None


class BusinessInsightsOut(BaseModel):
    business_id:   int
    business_name: str
    categories:    list[CategoryInsight]


class ReviewOut(BaseModel):
    review_id:     int
    reviewer_name: str | None
    rating:        float | None
    content:       str
    review_date:   date | None
    sentiments:    dict[str, str]


class SummaryOut(BaseModel):
    total_businesses: int
    total_reviews:    int
    total_analyzed:   int
    overall_positive: float
    overall_neutral:  float
    overall_negative: float
