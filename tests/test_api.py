import pytest
from db.models import Business, Review, Category, AnalysisResult, InsightsSummary


def make_business(db, name="Pho 24", btype="restaurant"):
    b = Business(name=name, type=btype, city="Hanoi", source="mock")
    db.add(b); db.flush()
    return b

def make_review(db, business_id, content="Đồ ăn ngon, phục vụ tốt.", rating=4.5):
    r = Review(business_id=business_id, content=content, rating=rating, source="mock")
    db.add(r); db.flush()
    return r

def make_analysis(db, review_id, category_name, sentiment="positive", confidence=0.9):
    cat = db.query(Category).filter_by(name=category_name).first()
    ar  = AnalysisResult(
        review_id=review_id, category_id=cat.id,
        sentiment=sentiment, confidence_score=confidence,
        strength_text="Tốt", weakness_text=None,
    )
    db.add(ar); db.flush()
    return ar

def make_insight(db, business_id, category_name, pct_pos=70, pct_neu=20, pct_neg=10):
    cat = db.query(Category).filter_by(name=category_name).first()
    ins = InsightsSummary(
        business_id=business_id, category_id=cat.id,
        total_reviews=10,
        pct_positive=pct_pos, pct_neutral=pct_neu, pct_negative=pct_neg,
    )
    db.add(ins); db.flush()
    return ins


class TestHealthCheck:
    def test_health(self, api_client):
        resp = api_client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestBusinessEndpoints:
    def test_list_empty(self, api_client):
        assert api_client.get("/api/v1/businesses").json() == []

    def test_list_returns_data(self, api_client, db_session):
        make_business(db_session, "Pho 24")
        make_business(db_session, "Bun Bo Hue")
        assert len(api_client.get("/api/v1/businesses").json()) == 2

    def test_get_not_found(self, api_client):
        assert api_client.get("/api/v1/businesses/9999").status_code == 404

    def test_get_found(self, api_client, db_session):
        b    = make_business(db_session)
        resp = api_client.get(f"/api/v1/businesses/{b.id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Pho 24"

    def test_response_schema(self, api_client, db_session):
        b    = make_business(db_session)
        data = api_client.get(f"/api/v1/businesses/{b.id}").json()
        for field in ["id", "name", "type", "city", "source"]:
            assert field in data


class TestInsightsEndpoint:
    def test_no_data_returns_404(self, api_client, db_session):
        b = make_business(db_session)
        assert api_client.get(f"/api/v1/businesses/{b.id}/insights").status_code == 404

    def test_returns_categories(self, api_client, db_session):
        b = make_business(db_session)
        make_insight(db_session, b.id, "Food")
        make_insight(db_session, b.id, "Service")
        resp = api_client.get(f"/api/v1/businesses/{b.id}/insights")
        assert resp.status_code == 200
        assert len(resp.json()["categories"]) == 2

    def test_percentage_fields(self, api_client, db_session):
        b = make_business(db_session)
        make_insight(db_session, b.id, "Food", pct_pos=70, pct_neu=20, pct_neg=10)
        cat = api_client.get(f"/api/v1/businesses/{b.id}/insights").json()["categories"][0]
        assert cat["pct_positive"] == 70.0
        assert cat["pct_neutral"]  == 20.0
        assert cat["pct_negative"] == 10.0

    def test_business_not_found(self, api_client):
        assert api_client.get("/api/v1/businesses/9999/insights").status_code == 404


class TestReviewsEndpoint:
    def test_empty(self, api_client, db_session):
        b = make_business(db_session)
        assert api_client.get(f"/api/v1/businesses/{b.id}/reviews").json() == []

    def test_returns_data(self, api_client, db_session):
        b = make_business(db_session)
        make_review(db_session, b.id)
        make_review(db_session, b.id)
        assert len(api_client.get(f"/api/v1/businesses/{b.id}/reviews").json()) == 2

    def test_with_sentiments(self, api_client, db_session):
        b = make_business(db_session)
        r = make_review(db_session, b.id)
        make_analysis(db_session, r.id, "Food", sentiment="positive")
        data = api_client.get(f"/api/v1/businesses/{b.id}/reviews").json()
        assert data[0]["sentiments"].get("Food") == "positive"

    def test_pagination_limit(self, api_client, db_session):
        b = make_business(db_session)
        for i in range(5):
            make_review(db_session, b.id, content=f"Review {i} nội dung đủ dài để pass")
        assert len(api_client.get(f"/api/v1/businesses/{b.id}/reviews?limit=3").json()) == 3

    def test_pagination_offset(self, api_client, db_session):
        b = make_business(db_session)
        for i in range(5):
            make_review(db_session, b.id, content=f"Review {i} nội dung đủ dài để pass")
        resp = api_client.get(f"/api/v1/businesses/{b.id}/reviews?limit=5&offset=3")
        assert len(resp.json()) == 2

    def test_business_not_found(self, api_client):
        assert api_client.get("/api/v1/businesses/9999/reviews").status_code == 404


class TestSummaryEndpoint:
    def test_empty_db(self, api_client):
        data = api_client.get("/api/v1/summary").json()
        assert data["total_businesses"] == 0
        assert data["total_reviews"]    == 0
        assert data["total_analyzed"]   == 0
        assert data["overall_positive"] == 0.0

    def test_with_data(self, api_client, db_session):
        b = make_business(db_session)
        r = make_review(db_session, b.id)
        make_analysis(db_session, r.id, "Food", sentiment="positive")
        data = api_client.get("/api/v1/summary").json()
        assert data["total_businesses"] == 1
        assert data["total_reviews"]    == 1
        assert data["total_analyzed"]   == 1

    def test_percentage_sum_is_100(self, api_client, db_session):
        b = make_business(db_session)
        r = make_review(db_session, b.id)
        make_analysis(db_session, r.id, "Food",    sentiment="positive")
        make_analysis(db_session, r.id, "Service", sentiment="negative")
        data  = api_client.get("/api/v1/summary").json()
        total = data["overall_positive"] + data["overall_neutral"] + data["overall_negative"]
        assert abs(total - 100.0) < 0.1
