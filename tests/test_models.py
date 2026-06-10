import pytest
from sqlalchemy.exc import IntegrityError
from db.models import Business, Review, Category, AnalysisResult


def test_business_creation(db_session):
    b = Business(name="Pho 24", type="restaurant", city="Hanoi", source="mock")
    db_session.add(b); db_session.flush()
    assert b.id is not None
    assert b.name == "Pho 24"


def test_review_fk_cascade(db_session):
    b = Business(name="Test Hotel", type="hotel", city="HCMC", source="mock")
    db_session.add(b); db_session.flush()
    r = Review(business_id=b.id, content="Great stay!", rating=4.5, source="mock")
    db_session.add(r); db_session.flush()
    review_id = r.id

    db_session.delete(b)
    db_session.flush()

    assert db_session.query(Review).filter_by(id=review_id).first() is None


def test_analysis_result_unique_constraint(db_session):
    b = Business(name="Test", type="cafe", city="DN", source="mock")
    db_session.add(b); db_session.flush()
    r = Review(business_id=b.id, content="Good coffee", rating=4.0, source="mock")
    db_session.add(r); db_session.flush()

    cat = db_session.query(Category).filter_by(name="Food").first()
    ar1 = AnalysisResult(review_id=r.id, category_id=cat.id, sentiment="positive", confidence_score=0.9)
    db_session.add(ar1); db_session.flush()

    ar2 = AnalysisResult(review_id=r.id, category_id=cat.id, sentiment="negative", confidence_score=0.8)
    db_session.add(ar2)

    with pytest.raises(IntegrityError):
        db_session.flush()
