import cv2
import easyocr
import requests
import numpy as np
import re

API_URL = "http://127.0.0.1:8000/api/detect"
reader = easyocr.Reader(['en'], gpu=False)  # change to True if you have CUDA

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Cannot open camera")
    exit()

frame_count = 0
last_plate = None

print("🎥 Camera started... Press 'q' to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    frame = cv2.resize(frame, (480, 360))

    # Process OCR every 10th frame only
    if frame_count % 10 != 0:
        cv2.imshow("Plate Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue

    # Focus on ROI (bottom center)
    h, w, _ = frame.shape
    roi = frame[int(h*0.5):h, int(w*0.2):int(w*0.8)]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    results = reader.readtext(gray, detail=1, paragraph=False)

    for (bbox, text, prob) in results:
        plate = re.sub(r'[^A-Z0-9]', '', text.upper())
        if 5 <= len(plate) <= 10:
            if plate != last_plate:
                try:
                    response = requests.post(API_URL, json={"plate_number": plate})
                    data = response.json()
                    status = data.get("status", "Unknown")
                    last_plate = plate
                except Exception as e:
                    print("API Error:", e)
                    status = "API Error"

            color = (0, 255, 0) if "✅" in status else (0, 0, 255)
            cv2.putText(frame, f"{plate} {status}", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    cv2.imshow("Plate Recognition", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
