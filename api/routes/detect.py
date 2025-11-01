from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.database import SessionLocal
from api import models, schemas
from datetime import datetime
from api.websocket_manager import manager

router = APIRouter()

# Dependency for DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🧠 Detect a plate number
@router.post("/", response_model=dict)
async def detect_plate(data: dict, db: Session = Depends(get_db)):
    plate_number = data.get("plate_number")
    if not plate_number:
        return {"error": "No plate_number provided"}

    # Check if vehicle is registered
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.plate_number == plate_number).first()

    # Prepare log entry
    timestamp = datetime.utcnow()
    if vehicle:
        new_log = models.Log(
            plate_number=plate_number,
            status="registered",
            vehicle_id=vehicle.id,
            timestamp=timestamp
        )
        db.add(new_log)
        db.commit()
        db.refresh(new_log)

        # 🔔 Notify all connected dashboards in real time
        await manager.broadcast({
            "plate_number": plate_number,
            "status": "registered",
            "timestamp": timestamp.isoformat(),
            "vehicle": {
                "name": vehicle.name,
                "purpose": vehicle.purpose
            }
        })

        return {
            "status": "✅ Registered",
            "vehicle": {
                "name": vehicle.name,
                "plate_number": vehicle.plate_number,
                "purpose": vehicle.purpose,
                "date_registered": vehicle.date_registered
            }
        }

    else:
        new_log = models.Log(
            plate_number=plate_number,
            status="unregistered",
            timestamp=timestamp
        )
        db.add(new_log)
        db.commit()
        db.refresh(new_log)

        # 🔔 Notify dashboard about unregistered detection
        await manager.broadcast({
            "plate_number": plate_number,
            "status": "unregistered",
            "timestamp": timestamp.isoformat()
        })

        return {"status": "🚫 Unregistered"}
