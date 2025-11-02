import cv2
from fastapi import APIRouter
from starlette.responses import StreamingResponse
import easyocr
import re
from api.database import SessionLocal
from api import models
from datetime import datetime
from api.websocket_manager import manager
import asyncio
import pytz

# Philippine timezone
PHILIPPINE_TZ = pytz.timezone('Asia/Manila')

router = APIRouter()

CAMERA_SOURCE = 0  # change if you have multiple cameras

# Initialize EasyOCR reader (match realtime_detection.py)
reader = easyocr.Reader(['en'], gpu=False)
print("✅ EasyOCR reader initialized")

# Track last detected plate to avoid duplicates (match realtime_detection.py)
last_plate = None

# Global camera instance
camera = None
camera_active = False

# Store pending detections for async processing
pending_plates = []
plate_processor_task = None

def release_camera():
    """Release the camera properly"""
    global camera, camera_active
    if camera is not None:
        camera.release()
        camera = None
        camera_active = False
        print("🛑 Camera released")

async def process_detection(plate: str):
    """Process detected plate and broadcast to WebSocket clients"""
    # Don't check for duplicates here - already handled in generate_frames()

    # Get DB session
    db = SessionLocal()
    try:
        # Check if vehicle is registered
        vehicle = db.query(models.Vehicle).filter(models.Vehicle.plate_number == plate).first()

        timestamp = datetime.now(PHILIPPINE_TZ)

        if vehicle:
            # Create log for registered vehicle
            new_log = models.Log(
                plate_number=plate,
                status="registered",
                vehicle_id=vehicle.id,
                timestamp=timestamp
            )
            db.add(new_log)
            db.commit()

            # Broadcast to WebSocket
            message = {
                "plate_number": plate,
                "status": "registered",
                "timestamp": timestamp.isoformat(),
                "vehicle": {
                    "name": vehicle.name,
                    "purpose": vehicle.purpose,
                    "profile_picture": vehicle.profile_picture
                }
            }
            await manager.broadcast(message)
            print(f"✅ Registered: {plate} - {vehicle.name}")
            print(f"📡 WebSocket broadcast sent: {message}")
        else:
            # Create log for unregistered vehicle
            new_log = models.Log(
                plate_number=plate,
                status="unregistered",
                timestamp=timestamp
            )
            db.add(new_log)
            db.commit()

            # Broadcast to WebSocket
            message = {
                "plate_number": plate,
                "status": "unregistered",
                "timestamp": timestamp.isoformat()
            }
            await manager.broadcast(message)
            print(f"🚫 Unregistered: {plate}")
            print(f"📡 WebSocket broadcast sent: {message}")
    except Exception as e:
        print(f"❌ Error processing detection: {e}")
    finally:
        db.close()

def generate_frames():
    """
    Generate frames for streaming - matches realtime_detection.py logic exactly
    """
    global camera, camera_active, last_plate, pending_plates

    # Initialize camera
    if camera is None:
        camera = cv2.VideoCapture(CAMERA_SOURCE)
        camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer to minimize lag
        camera.set(cv2.CAP_PROP_FPS, 30)  # Set frame rate
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set resolution
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not camera.isOpened():
        print("❌ Cannot open camera")
        release_camera()
        return

    camera_active = True
    frame_count = 0
    print("🎥 Camera stream started with plate detection")

    try:
        while camera_active:
            ret, frame = camera.read()
            if not ret:
                print("⚠️ Failed to read frame")
                break

            frame_count += 1

            # Resize frame to smaller size for better performance
            frame = cv2.resize(frame, (640, 480))

            # Process OCR every 30th frame only (reduce OCR frequency for better performance)
            if frame_count % 30 == 0:
                try:
                    # Use only center ROI for better performance (don't process full frame)
                    h, w, _ = frame.shape

                    # Center ROI - where license plates are typically shown
                    roi = frame[int(h*0.3):int(h*0.7), int(w*0.2):int(w*0.8)]
                    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

                    # Process OCR only on ROI (faster than full frame)
                    results = reader.readtext(gray_roi, detail=1, paragraph=False)

                    # Debug: print all OCR results (reduce logging frequency)
                    if results and frame_count % 90 == 0:  # Print every 90 frames to avoid spam
                        print(f"🔍 OCR found {len(results)} text regions")
                        for (_, text, prob) in results:
                            print(f"   Raw: '{text}' | Confidence: {prob:.2f}")

                    best_plate = None
                    best_prob = 0

                    # Process all results and pick the best one
                    for (_, text, prob) in results:
                        # Clean the detected text
                        cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())

                        # Check if it looks like a valid plate (5-10 characters)
                        if 5 <= len(cleaned) <= 10:
                            # Prefer results with higher confidence and more digits
                            digit_count = sum(c.isdigit() for c in cleaned)

                            # Good plate should have mix of letters and numbers
                            if digit_count >= 1 and prob > best_prob:
                                best_plate = cleaned
                                best_prob = prob

                    # If we found a valid plate
                    if best_plate and best_plate != last_plate:
                        print(f"✅ Valid plate detected: {best_plate} (confidence: {best_prob:.2f})")
                        # Add to pending list for async processing
                        pending_plates.append(best_plate)
                        last_plate = best_plate

                        # Draw on frame
                        cv2.putText(frame, f"{best_plate}", (30, 40),
                                  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                except Exception as e:
                    print(f"❌ OCR Error: {e}")

            # Encode frame to JPEG with lower quality for faster streaming
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 60]
            _, buffer = cv2.imencode('.jpg', frame, encode_param)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    except GeneratorExit:
        print("🔌 Client disconnected")
    finally:
        release_camera()

async def process_pending_plates():
    """Background task to process pending plate detections"""
    global camera_active, pending_plates

    print("🔄 Pending plates processor started")

    while camera_active:
        if pending_plates:
            plate = pending_plates.pop(0)
            print(f"📤 Processing plate from queue: {plate}")
            await process_detection(plate)
        else:
            await asyncio.sleep(0.1)

    print("🛑 Pending plates processor stopped")

@router.get("/video_feed")
async def video_feed():
    """Video feed endpoint with plate detection"""
    global plate_processor_task, camera_active

    print("📡 /api/video_feed accessed")

    camera_active = True  # Ensure camera is active

    # Start background task to process pending plates (only if not already running)
    if plate_processor_task is None or plate_processor_task.done():
        plate_processor_task = asyncio.create_task(process_pending_plates())
        print("✅ Plate processor task started")
    else:
        print("ℹ️ Plate processor task already running")

    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@router.post("/stop_camera")
async def stop_camera():
    """Stop the camera stream"""
    global camera_active
    camera_active = False
    release_camera()
    await asyncio.sleep(0.5)  # Give time for cleanup
    return {"status": "Camera stopped"}
