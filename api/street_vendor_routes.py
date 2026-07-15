from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from db.street_vendor_models import StreetVendor
from api.street_vendor_schemas import StreetVendorCreate, StreetVendorResponse

router = APIRouter(prefix="/api/v1/street-vendors", tags=["street-vendors"])


@router.get("/", response_model=list[StreetVendorResponse])
def get_all_vendors(db: Session = Depends(get_db)):
    return db.query(StreetVendor).all()


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
