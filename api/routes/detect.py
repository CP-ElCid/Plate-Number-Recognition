from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from api.database import SessionLocal
from api import models
from datetime import datetime
from api.websocket_manager import manager
import easyocr
import numpy as np
import cv2
import re
import pytz

# Philippine timezone
PHILIPPINE_TZ = pytz.timezone('Asia/Manila')

router = APIRouter()

# Initialize EasyOCR reader (do this once to avoid reloading model each time)
reader = easyocr.Reader(['en'], gpu=False)

# Dependency for DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🖼️ Process image and extract plate number using EasyOCR
def extract_plate_from_image(image_bytes: bytes) -> str | None:
    """
    Extract license plate number from image using EasyOCR.
    Returns None if no valid plate is detected.
    """
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            print("❌ Failed to decode image")
            return None

        # Use EasyOCR to detect text
        results = reader.readtext(img)

        print(f"🔍 OCR Results: {results}")

        # Look for text that resembles a license plate
        # License plates are typically: 2-3 letters + 3-4 numbers or similar patterns
        for (_, text, confidence) in results:
            # Clean up the text
            text = text.upper().replace(' ', '').replace('-', '')

            # Check if it looks like a plate number (alphanumeric, 5-8 characters)
            if confidence > 0.3 and len(text) >= 5 and len(text) <= 8:
                # Check if it's alphanumeric
                if re.match(r'^[A-Z0-9]+$', text):
                    print(f"✅ Found potential plate: {text} (confidence: {confidence:.2f})")
                    return text

        print("⚠️ No valid plate detected in image")
        return None

    except Exception as e:
        print(f"❌ OCR Error: {e}")
        return None

# 🧠 Detect plate from image
@router.post("/", response_model=dict)
async def detect_plate_from_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        print(f"📸 Received image file: {file.filename}, size: {file.size}")

        # Read image file
        image_bytes = await file.read()
        print(f"📸 Image bytes read: {len(image_bytes)} bytes")

        # Extract plate number from image using OCR
        plate_number = extract_plate_from_image(image_bytes)
        print(f"🔍 Detected plate number: {plate_number}")

        if not plate_number:
            # No plate detected - return success but don't save/broadcast
            return {"status": "no_plate", "message": "No plate detected in image"}

        # Check if vehicle is registered
        vehicle = db.query(models.Vehicle).filter(models.Vehicle.plate_number == plate_number).first()

        # Prepare log entry with Philippine time
        timestamp = datetime.now(PHILIPPINE_TZ)
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
                    "purpose": vehicle.purpose,
                    "profile_picture": vehicle.profile_picture
                }
            })

            return {
                "plate_number": plate_number,
                "status": "registered",
                "timestamp": timestamp.isoformat(),
                "vehicle": {
                    "name": vehicle.name,
                    "plate_number": vehicle.plate_number,
                    "purpose": vehicle.purpose,
                    "profile_picture": vehicle.profile_picture,
                    "date_registered": str(vehicle.date_registered)
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

            return {
                "plate_number": plate_number,
                "status": "unregistered",
                "timestamp": timestamp.isoformat()
            }

    except Exception as e:
        return {"error": f"Failed to process image: {str(e)}"}

# 🧠 Detect a plate number (manual entry)
@router.post("/manual", response_model=dict)
async def detect_plate(data: dict, db: Session = Depends(get_db)):
    plate_number = data.get("plate_number")
    if not plate_number:
        return {"error": "No plate_number provided"}

    # Normalize plate number: uppercase, remove spaces and special characters
    plate_number = plate_number.upper().replace(' ', '').replace('-', '')

    # Check if vehicle is registered (case-insensitive)
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.plate_number == plate_number).first()

    # Manual checks don't create logs automatically
    # User can choose to add to logs via the "Add to Logs Now" button
    timestamp = datetime.now(PHILIPPINE_TZ)

    if vehicle:
        return {
            "plate_number": plate_number,
            "status": "registered",
            "timestamp": timestamp.isoformat(),
            "vehicle": {
                "name": vehicle.name,
                "plate_number": vehicle.plate_number,
                "purpose": vehicle.purpose,
                "profile_picture": vehicle.profile_picture,
                "date_registered": str(vehicle.date_registered)
            }
        }
    else:
        return {
            "plate_number": plate_number,
            "status": "unregistered",
            "timestamp": timestamp.isoformat()
        }
