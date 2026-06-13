from sqlalchemy import (
    Column, Integer, String, Text, Numeric,
    Date, ForeignKey, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import ARRAY, TIMESTAMP
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Business(Base):
    __tablename__ = "businesses"

    id         = Column(Integer, primary_key=True)
    name       = Column(String(255), nullable=False)
    type       = Column(String(50),  nullable=False)   # restaurant | hotel | cafe | other
    address    = Column(Text)
    city       = Column(String(100))
    source     = Column(String(50), default="yelp")    # yelp | mock | manual
    created_at = Column(TIMESTAMP, server_default=func.now())

    reviews  = relationship("Review",          back_populates="business", cascade="all, delete-orphan")
    insights = relationship("InsightsSummary", back_populates="business", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"

    id          = Column(Integer, primary_key=True)
    name        = Column(String(100), nullable=False, unique=True)
    description = Column(Text)


class Review(Base):
    __tablename__ = "reviews"

    id            = Column(Integer, primary_key=True)
    business_id   = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    reviewer_name = Column(String(255))
    rating        = Column(Numeric(2, 1))
    content       = Column(Text, nullable=False)
    review_date   = Column(Date)
    source        = Column(String(50), default="yelp")
    created_at    = Column(TIMESTAMP, server_default=func.now())

    business         = relationship("Business",       back_populates="reviews")
    analysis_results = relationship("AnalysisResult", back_populates="review", cascade="all, delete-orphan")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    __table_args__ = (UniqueConstraint("review_id", "category_id"),)

    id               = Column(Integer, primary_key=True)
    review_id        = Column(Integer, ForeignKey("reviews.id",   ondelete="CASCADE"), nullable=False)
    category_id      = Column(Integer, ForeignKey("categories.id"), nullable=False)
    sentiment        = Column(String(20), nullable=False)   # positive | neutral | negative
    strength_text    = Column(Text)
    weakness_text    = Column(Text)
    confidence_score = Column(Numeric(4, 3))
    analyzed_at      = Column(TIMESTAMP, server_default=func.now())

    review   = relationship("Review",   back_populates="analysis_results")
    category = relationship("Category")


class InsightsSummary(Base):
    __tablename__ = "insights_summary"
    __table_args__ = (UniqueConstraint("business_id", "category_id"),)

    id             = Column(Integer, primary_key=True)
    business_id    = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    category_id    = Column(Integer, ForeignKey("categories.id"), nullable=False)
    total_reviews  = Column(Integer, default=0)
    pct_positive   = Column(Numeric(5, 2), default=0)
    pct_neutral    = Column(Numeric(5, 2), default=0)
    pct_negative   = Column(Numeric(5, 2), default=0)
    top_strengths  = Column(ARRAY(Text))
    top_weaknesses = Column(ARRAY(Text))
    updated_at     = Column(TIMESTAMP, server_default=func.now())

    business = relationship("Business", back_populates="insights")
    category = relationship("Category")
