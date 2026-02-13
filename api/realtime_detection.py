import cv2
import easyocr
import requests
import numpy as np
import re
from datetime import datetime

API_URL = "http://127.0.0.1:8000/api/detect/manual"
# Load reader once
reader = easyocr.Reader(['en'], gpu=False)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("ERROR: Cannot open camera")
    exit()

# --- Detection Constants ---
CONFIDENCE_THRESHOLD = 0.70
BUFFER_SIZE = 5
VERIFICATION_COUNT = 3
COOLDOWN_SECONDS = 30

# --- State ---
plate_buffer = []
logged_plates = {}
last_plate = None
frame_count = 0

print("Camera started... Press 'q' to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    frame = cv2.resize(frame, (640, 480))

    # Process OCR every 15th frame
    if frame_count % 15 != 0:
        cv2.imshow("Plate Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue

    # ROI (Center Focus)
    h, w, _ = frame.shape
    roi = frame[int(h*0.3):int(h*0.7), int(w*0.2):int(w*0.8)]
    
    # Preprocessing
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # Sharpen
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    enhanced = cv2.filter2D(enhanced, -1, kernel)

    results = reader.readtext(enhanced, detail=1, paragraph=False)

    best_plate = None
    best_prob = 0

    if results:
        # 1. Segment Merging
        segments = []
        for (bbox, text, prob) in results:
            cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
            if prob >= 0.25 and len(cleaned) > 0:
                x0 = bbox[0][0]
                y_center = (bbox[0][1] + bbox[2][1]) / 2
                x_end = bbox[1][0]
                segments.append({'text': cleaned, 'x0': x0, 'x_end': x_end, 'y': y_center, 'prob': prob})
        
        segments.sort(key=lambda s: s['x0'])
        
        merged = []
        if segments:
            curr = segments[0]
            for i in range(1, len(segments)):
                next_s = segments[i]
                if abs(next_s['y'] - curr['y']) < 30 and (next_s['x0'] - curr['x_end']) < 100:
                    curr['text'] += next_s['text']
                    curr['x_end'] = next_s['x_end']
                    curr['prob'] = (curr['prob'] + next_s['prob']) / 2
                else:
                    merged.append(curr)
                    curr = next_s
            merged.append(curr)

        # 2. Filtering
        for cand in merged:
            text = cand['text']
            prob = cand['prob']
            if (4 <= len(text) <= 10 and prob >= CONFIDENCE_THRESHOLD and any(c.isdigit() for c in text)):
                if prob > best_prob:
                    best_plate = text
                    best_prob = prob

    # 3. Temporal Verification & API Call
    if best_plate:
        plate_buffer.append(best_plate)
        if len(plate_buffer) > BUFFER_SIZE:
            plate_buffer.pop(0)

        occurrences = plate_buffer.count(best_plate)
        if occurrences >= VERIFICATION_COUNT:
            current_time = datetime.now()
            last_log = logged_plates.get(best_plate)
            
            if last_log is None or (current_time - last_log).total_seconds() > COOLDOWN_SECONDS:
                try:
                    # Send to manual endpoint (which we also updated to skip unregistered broadcasts)
                    response = requests.post(API_URL, json={"plate_number": best_plate})
                    data = response.json()
                    status = data.get("status", "Unknown")
                    logged_plates[best_plate] = current_time
                    print(f"✅ Processed: {best_plate} (Status: {status})")
                except Exception as e:
                    print("API Error:", e)

        # Show verification status on frame
        color = (0, 255, 0) if occurrences >= VERIFICATION_COUNT else (0, 165, 255)
        cv2.putText(frame, f"{best_plate} ({occurrences}/{VERIFICATION_COUNT})", 
                    (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    cv2.imshow("Plate Recognition", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
