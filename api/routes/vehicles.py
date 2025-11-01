from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.database import SessionLocal
from api import models, schemas


router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[schemas.Vehicle])
def get_vehicles(db: Session = Depends(get_db)):
    vehicles = db.query(models.Vehicle).all()
    return vehicles

@router.post("/", response_model=schemas.Vehicle, status_code=status.HTTP_201_CREATED)
def create_vehicle(vehicle: schemas.VehicleCreate, db: Session = Depends(get_db)):
    # Check if plate number already exists
    existing = db.query(models.Vehicle).filter(models.Vehicle.plate_number == vehicle.plate_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Vehicle already registered")

    new_vehicle = models.Vehicle(
        name=vehicle.name,
        plate_number=vehicle.plate_number,
        purpose=vehicle.purpose,
        profile_picture=vehicle.profile_picture
    )
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)
    return new_vehicle

@router.get("/{plate_number}", response_model=schemas.Vehicle)
def get_vehicle_by_plate(plate_number: str, db: Session = Depends(get_db)):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.plate_number == plate_number).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.put("/{plate_number}", response_model=schemas.Vehicle)
def update_vehicle(plate_number: str, updated_data: schemas.VehicleCreate, db: Session = Depends(get_db)):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.plate_number == plate_number).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    vehicle.name = updated_data.name
    vehicle.purpose = updated_data.purpose
    vehicle.profile_picture = updated_data.profile_picture

    db.commit()
    db.refresh(vehicle)
    return vehicle

@router.delete("/{plate_number}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(plate_number: str, db: Session = Depends(get_db)):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.plate_number == plate_number).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    db.delete(vehicle)
    db.commit()
    return {"message": "Vehicle deleted"}
