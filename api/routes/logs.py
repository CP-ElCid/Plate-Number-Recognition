from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.database import SessionLocal
from api import models, schemas
from datetime import datetime
import pytz

# Philippine timezone
PHILIPPINE_TZ = pytz.timezone('Asia/Manila')

router = APIRouter()

# DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🧾 Get all logs
@router.get("/", response_model=list[schemas.Log])
def get_logs(db: Session = Depends(get_db)):
    logs = db.query(models.Log).order_by(models.Log.timestamp.desc()).all()
    return logs

# 🪪 Create a new log
@router.post("/", response_model=schemas.Log, status_code=status.HTTP_201_CREATED)
def create_log(log: schemas.LogCreate, db: Session = Depends(get_db)):
    # If vehicle_id is not provided, look it up by plate_number
    vehicle_id = log.vehicle_id
    if not vehicle_id:
        vehicle = db.query(models.Vehicle).filter(
            models.Vehicle.plate_number == log.plate_number
        ).first()
        if vehicle:
            vehicle_id = vehicle.id

    new_log = models.Log(
        plate_number=log.plate_number,
        status=log.status,
        vehicle_id=vehicle_id,
        timestamp=datetime.now(PHILIPPINE_TZ)
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

# 🗑️ Clear all logs
@router.delete("/clear", status_code=status.HTTP_204_NO_CONTENT)
def clear_all_logs(db: Session = Depends(get_db)):
    """Delete all logs from the database"""
    try:
        db.query(models.Log).delete()
        db.commit()
        return {"message": "All logs cleared successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear logs: {str(e)}")
