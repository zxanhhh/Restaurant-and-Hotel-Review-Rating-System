from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from math import radians, sin, cos, sqrt, atan2
from db.database import get_db
from db.street_vendor_models import StreetVendor
from api.street_vendor_schemas import StreetVendorCreate, StreetVendorResponse

router = APIRouter(prefix="/api/v1/street-vendors", tags=["street-vendors"])


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))


@router.get("/", response_model=list[StreetVendorResponse])
def get_all_vendors(db: Session = Depends(get_db)):
    return db.query(StreetVendor).all()


@router.get("/nearby")
def get_nearby_vendors(
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(2.0),
    db: Session = Depends(get_db),
):
    all_vendors = db.query(StreetVendor).all()
    nearby = []
    for v in all_vendors:
        dist = haversine_distance(lat, lng, v.lat, v.lng)
        if dist <= radius_km:
            nearby.append({
                "id": v.id,
                "name": v.name,
                "category": v.category,
                "lat": v.lat,
                "lng": v.lng,
                "landmark_note": v.landmark_note,
                "time_note": v.time_note,
                "price_range": v.price_range,
                "has_thuoc_lao": v.has_thuoc_lao,
                "distance_km": round(dist, 2),
            })
    nearby.sort(key=lambda x: x["distance_km"])
    return nearby


@router.post("/", response_model=StreetVendorResponse)
def create_vendor(vendor: StreetVendorCreate, db: Session = Depends(get_db)):
    new_vendor = StreetVendor(**vendor.model_dump())
    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)
    return new_vendor


@router.get("/{vendor_id}", response_model=StreetVendorResponse)
def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    return db.query(StreetVendor).filter(StreetVendor.id == vendor_id).first()
