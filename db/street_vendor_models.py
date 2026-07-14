from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, func
from db.database import Base


class StreetVendor(Base):
    __tablename__ = "street_vendors"

    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String, nullable=False)
    category        = Column(String, nullable=False)   # "Trà đá" | "Nước mía" | "Xe đẩy" ...
    lat             = Column(Float, nullable=False)
    lng             = Column(Float, nullable=False)
    landmark_note   = Column(String, nullable=True)
    time_note       = Column(String, nullable=True)     # "Chiều đến khuya"
    price_range     = Column(String, nullable=True)     # "5-10k"
    has_thuoc_lao   = Column(Boolean, default=False)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
