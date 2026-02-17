import cv2
from fastapi import APIRouter
from starlette.responses import StreamingResponse
import easyocr
import re
import numpy as np
from api.database import SessionLocal
from api import models
from datetime import datetime
from api.websocket_manager import manager
from api.esp32_controller import trigger_esp32
import asyncio
import pytz
from api.config import (
    CAMERA_SOURCE, 
    CONFIDENCE_THRESHOLD, 
    BUFFER_SIZE, 
    VERIFICATION_COUNT, 
    COOLDOWN_SECONDS, 
    OCR_FRAME_INTERVAL,
    USE_GPU
)

# Philippine timezone
PHILIPPINE_TZ = pytz.timezone('Asia/Manila')

router = APIRouter()

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'], gpu=USE_GPU)
print(f"✅ EasyOCR reader initialized (GPU: {USE_GPU})")

# --- Detection Constants ---
# Imported from api.config
# CONFIDENCE_THRESHOLD = 0.60
# BUFFER_SIZE = 5      
# VERIFICATION_COUNT = 3
# COOLDOWN_SECONDS = 30
# OCR_FRAME_INTERVAL = 15

# --- State ---

# --- State ---
plate_buffer = []            # Rolling buffer of recent plate reads
logged_plates = {}           # {plate: datetime} cooldown tracker

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

def preprocess_roi(roi):
    """
    Advanced preprocessing for better OCR accuracy:
    1. Grayscale conversion
    2. CLAHE (Contrast Limited Adaptive Histogram Equalization)
    3. Sharpening kernel
    """
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # CLAHE enhances local contrast — critical for plates in shadow / glare
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Sharpening makes character edges crisper for OCR
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    enhanced = cv2.filter2D(enhanced, -1, kernel)

    return enhanced

def merge_segments(results):
    """
    Merge adjacent OCR text segments that belong to the same plate.
    E.g. 'DBA' + '4658' on the same line → 'DBA4658'
    """
    segments = []
    for (bbox, text, prob) in results:
        cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
        if prob >= 0.25 and len(cleaned) > 0:
            x0 = bbox[0][0]
            y_center = (bbox[0][1] + bbox[2][1]) / 2
            x_end = bbox[1][0]
            segments.append({
                'text': cleaned,
                'x0': x0,
                'x_end': x_end,
                'y': y_center,
                'prob': prob
            })

    # Sort left-to-right
    segments.sort(key=lambda s: s['x0'])

    merged = []
    if segments:
        curr = segments[0].copy()
        for i in range(1, len(segments)):
            next_s = segments[i]
            # Same horizontal line (Y within 30px) and close together (X gap < 100px)
            if abs(next_s['y'] - curr['y']) < 30 and (next_s['x0'] - curr['x_end']) < 100:
                curr['text'] += next_s['text']
                curr['x_end'] = next_s['x_end']
                curr['prob'] = (curr['prob'] + next_s['prob']) / 2
            else:
                merged.append(curr)
                curr = next_s.copy()
        merged.append(curr)

    return merged

def find_best_plate(merged_segments):
    """
    From merged OCR segments, find the best plate candidate:
    - 4-10 alphanumeric characters
    - At least 1 digit
    - Highest confidence wins
    """
    best_plate = None
    best_prob = 0

    for cand in merged_segments:
        text = cand['text']
        prob = cand['prob']
        if (4 <= len(text) <= 10
                and prob >= CONFIDENCE_THRESHOLD
                and any(c.isdigit() for c in text)):
            if prob > best_prob:
                best_plate = text
                best_prob = prob

    return best_plate, best_prob

async def process_detection(plate: str):
    """Process detected plate: log to DB, broadcast ONLY registered plates via WebSocket"""
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

            # Broadcast to WebSocket (REGISTERED ONLY) - Send FIRST for instant UI update
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

            # Trigger ESP32 - Green LED + short beep (Non-blocking attempt)
            try:
                # We use create_task to let it run in background if we wanted, 
                # but simply awaiting it AFTER broadcast is enough to unblock UI.
                # Adding a separate try-block ensures hardware errors don't crash the loop.
                await trigger_esp32("registered")
            except Exception as e:
                print(f"⚠️ ESP32 Trigger Failed (UI updated anyway): {e}")
        else:
            # Create log for unregistered vehicle (still saved to DB)
            new_log = models.Log(
                plate_number=plate,
                status="unregistered",
                timestamp=timestamp
            )
            db.add(new_log)
            db.commit()

            # Trigger ESP32 - Red LED only (no buzzer, handled on ESP32 side)
            await trigger_esp32("unregistered")

            # NOTE: Skip WebSocket broadcast for unregistered plates
            print(f"🚫 Unregistered: {plate} (logged to DB, broadcast skipped)")
    except Exception as e:
        print(f"❌ Error processing detection: {e}")
    finally:
        db.close()

def generate_frames():
    """
    Generate frames for streaming with high-accuracy plate detection:
    - CLAHE + sharpening preprocessing
    - Segment merging for split plate text
    - Temporal verification buffer (3/5 reads required)
    - Cooldown to prevent duplicate logging
    """
    global camera, camera_active, pending_plates, plate_buffer, logged_plates

    # Initialize camera
    if camera is None:
        camera = cv2.VideoCapture(CAMERA_SOURCE)
        camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer to minimize lag
        camera.set(cv2.CAP_PROP_FPS, 30)         # Set frame rate
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not camera.isOpened():
        print("❌ Cannot open camera")
        release_camera()
        return

    camera_active = True
    frame_count = 0
    print("🎥 Camera stream started with high-accuracy plate detection")

    try:
        while camera_active:
            ret, frame = camera.read()
            if not ret:
                print("⚠️ Failed to read frame")
                break

            frame_count += 1

            # Resize frame
            frame = cv2.resize(frame, (640, 480))

            # Process OCR every Nth frame
            if frame_count % OCR_FRAME_INTERVAL == 0:
                try:
                    h, w, _ = frame.shape

                    # Center ROI — where license plates are typically visible
                    roi = frame[int(h * 0.3):int(h * 0.7), int(w * 0.2):int(w * 0.8)]

                    # Advanced preprocessing for better OCR accuracy
                    enhanced = preprocess_roi(roi)

                    # Run OCR on preprocessed ROI
                    results = reader.readtext(enhanced, detail=1, paragraph=False)

                    # Debug logging (every 45th frame to avoid spam)
                    if results and frame_count % 45 == 0:
                        print(f"🔍 OCR found {len(results)} text regions")
                        for (_, text, prob) in results:
                            print(f"   Raw: '{text}' | Confidence: {prob:.2f}")

                    # Merge adjacent text segments (e.g. 'DBA' + '4658')
                    merged = merge_segments(results)

                    # Find the best plate candidate
                    best_plate, best_prob = find_best_plate(merged)

                    # --- Temporal Verification ---
                    if best_plate:
                        plate_buffer.append(best_plate)
                        if len(plate_buffer) > BUFFER_SIZE:
                            plate_buffer.pop(0)

                        occurrences = plate_buffer.count(best_plate)

                        if occurrences >= VERIFICATION_COUNT:
                            # Plate confirmed — check cooldown
                            current_time = datetime.now()
                            last_log = logged_plates.get(best_plate)

                            if last_log is None or (current_time - last_log).total_seconds() > COOLDOWN_SECONDS:
                                # Queue for async processing
                                pending_plates.append(best_plate)
                                logged_plates[best_plate] = current_time
                                print(f"✅ Plate confirmed: {best_plate} ({occurrences}/{VERIFICATION_COUNT}, confidence: {best_prob:.2f})")

                        # Show verification status on frame
                        color = (0, 255, 0) if occurrences >= VERIFICATION_COUNT else (0, 165, 255)
                        cv2.putText(frame, f"{best_plate} ({occurrences}/{VERIFICATION_COUNT})",
                                    (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

                except Exception as e:
                    print(f"❌ OCR Error: {e}")

            # Encode frame to JPEG
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
