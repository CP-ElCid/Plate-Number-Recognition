from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.database import SessionLocal
from api import models, schemas
from datetime import datetime

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
    new_log = models.Log(
        plate_number=log.plate_number,
        status=log.status,
        vehicle_id=log.vehicle_id,
        timestamp=datetime.utcnow()
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log
