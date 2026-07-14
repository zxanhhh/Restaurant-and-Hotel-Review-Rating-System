from pydantic import BaseModel, ConfigDict
from typing import Optional


class StreetVendorCreate(BaseModel):
    name: str
    category: str
    lat: float
    lng: float
    landmark_note: Optional[str] = None
    time_note: Optional[str] = None
    price_range: Optional[str] = None
    has_thuoc_lao: bool = False


class StreetVendorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    lat: float
    lng: float
    landmark_note: Optional[str]
    time_note: Optional[str]
    price_range: Optional[str]
    has_thuoc_lao: bool
