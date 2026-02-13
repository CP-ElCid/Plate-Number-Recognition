# Troubleshooting Guide

## WebSocket Issues

### WebSocket Not Connecting After Restart

**Symptoms:**
- WebSocket shows as disconnected after restarting backend
- Frontend can't receive real-time updates
- Console shows WebSocket connection errors

**Solutions:**

#### 1. Port Already in Use
Check if the backend port is still occupied:

```bash
# Windows
netstat -ano | findstr :8000

# If port is in use, kill the process
taskkill /PID <PID_NUMBER> /F
```

#### 2. Proper Server Shutdown
The backend now includes automatic cleanup on shutdown:
- WebSocket connections are closed properly
- Camera is released automatically
- Resources are freed

**Just wait 2-3 seconds between restarts** to allow cleanup to complete.

#### 3. Kill All Python Processes
If issues persist:

```bash
# Windows
tasklist | findstr python.exe
taskkill /IM python.exe /F

# Then restart backend
uvicorn api.main:app --reload
```

#### 4. Frontend Reconnection
Make sure your frontend has WebSocket reconnection logic. Example:

```javascript
let ws;
let reconnectInterval;

function connectWebSocket() {
  ws = new WebSocket('ws://localhost:8000/ws/detections');

  ws.onopen = () => {
    console.log('WebSocket connected');
    clearInterval(reconnectInterval);
  };

  ws.onclose = () => {
    console.log('WebSocket disconnected, reconnecting...');
    // Attempt to reconnect every 3 seconds
    reconnectInterval = setInterval(() => {
      connectWebSocket();
    }, 3000);
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
}
```

### WebSocket Connection Drops Randomly

**Causes:**
- Network issues
- Long-running operations blocking the event loop
- Client timeout

**Solutions:**

1. **Add keepalive pings** (already implemented in backend)
2. **Check network stability**
3. **Verify no firewall blocking WebSocket**

### Check WebSocket Status

```bash
# Test WebSocket connection
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: test" \
  http://localhost:8000/ws/detections
```

Expected response: `101 Switching Protocols`

---

## ESP32 Issues

### ESP32 Not Connecting to WiFi

**Solutions:**

1. **Check WiFi credentials** in ESP32 code:
   ```python
   WIFI_SSID = "YOUR_WIFI_NAME"  # Double-check this
   WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"  # And this
   ```

2. **Check WiFi band** - ESP32 only supports 2.4GHz (not 5GHz)

3. **Check signal strength** - Move ESP32 closer to router

4. **Serial monitor** - Open Thonny and check console output for errors

### Backend Can't Reach ESP32

**Symptoms:**
- `❌ Cannot connect to ESP32`
- `⏱️ ESP32 request timeout`

**Solutions:**

1. **Verify IP address**:
   ```bash
   # Ping ESP32
   ping 192.168.1.100

   # Access web interface
   # Open browser: http://192.168.1.100
   ```

2. **Update IP in backend** (`api/esp32_controller.py`):
   ```python
   ESP32_IP = "192.168.1.100"  # Use actual IP from ESP32 console
   ```

3. **Check same network** - Computer and ESP32 must be on same WiFi

4. **Restart ESP32** - Press reset button or power cycle

5. **Check firewall** - Temporarily disable to test

### LEDs/Buzzer Not Working

**Check wiring:**
```
ESP32 GPIO 25 → 220Ω resistor → Green LED (+) → GND
ESP32 GPIO 26 → 220Ω resistor → Red LED (+) → GND
ESP32 GPIO 27 → Buzzer (+) → GND
```

**Common mistakes:**
- LED polarity reversed (long leg = positive/anode)
- Missing resistors (LEDs will burn out)
- Loose connections
- Wrong GPIO pins

**Test components individually** via ESP32 web interface:
- Go to `http://ESP32_IP`
- Click "Test All" button
- Each component should activate

---

## Camera Issues

### Camera Not Opening

**Symptoms:**
- `❌ Cannot open camera`
- Black screen in video feed
- Camera access denied

**Solutions:**

1. **Check camera source** in `api/camera_stream.py`:
   ```python
   CAMERA_SOURCE = 0  # Try 0, 1, 2 for different cameras
   ```

2. **Camera in use by another app**:
   ```bash
   # Close other apps using camera (Zoom, Teams, etc.)
   # Or restart computer
   ```

3. **Camera permissions**:
   - Windows: Settings → Privacy → Camera → Allow apps
   - Check if Python has camera permission

4. **Release camera properly**:
   ```bash
   # Stop camera endpoint
   curl -X POST http://localhost:8000/api/stop_camera
   ```

### Camera Stream Laggy

**Solutions:**

1. **Reduce frame processing** - Already optimized to process every 30 frames

2. **Lower resolution** in `camera_stream.py`:
   ```python
   camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # Lower from 640
   camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  # Lower from 480
   ```

3. **Reduce JPEG quality** (already at 60%):
   ```python
   encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 40]  # Lower quality
   ```

---

## Detection Issues

### Plates Not Being Detected

**Symptoms:**
- Camera working but no plate detection
- No logs being created

**Solutions:**

1. **Check OCR processing** - Look for console output:
   ```
   🔍 OCR found X text regions
   ```

2. **Plate must be in center ROI** - Position plate in middle 60% of frame

3. **Good lighting** - Ensure plate is well-lit and clear

4. **Valid format** - Plate must be 5-10 characters with mix of letters and numbers

5. **Check confidence threshold** - OCR results with low confidence are filtered

### Wrong Plate Detected

**Common causes:**
- Text on signs, stickers, etc.
- Reflections
- Poor OCR accuracy

**Solutions:**

1. **Adjust validation** in `camera_stream.py`:
   ```python
   # Line ~168: Adjust length requirements
   if 6 <= len(cleaned) <= 9:  # More strict (was 5-10)
   ```

2. **Increase confidence threshold**:
   ```python
   # Line ~173: Add confidence check
   if digit_count >= 2 and prob > 0.7:  # Require higher confidence
   ```

### Duplicate Detections

Already handled by `last_plate` tracking:
```python
if best_plate and best_plate != last_plate:
    # Only process if different from last detection
```

---

## Database Issues

### Database Locked

**Symptoms:**
- `database is locked` errors
- Operations timing out

**Solutions:**

1. **Close all connections**:
   ```python
   # Restart backend
   # SQLite only allows one writer at a time
   ```

2. **Check for orphaned connections**:
   ```bash
   # Delete database and restart (CAREFUL - loses data)
   # rm plate_system.db
   ```

---

## API Issues

### 404 Not Found

**Check endpoints** - Go to `http://localhost:8000/docs` for full API documentation

### CORS Errors

Already configured for localhost:
```python
allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
```

If frontend is on different port, add it to `api/main.py`:
```python
allow_origins=[
    "http://localhost:5173",
    "http://localhost:3000",  # Add your frontend port
]
```

---

## General Debugging

### Enable Verbose Logging

The system already has extensive logging. Check console output for:
- `✅` Success messages
- `❌` Error messages
- `📡` WebSocket broadcasts
- `🎥` Camera events
- `🔍` OCR detections

### Test Individual Components

1. **Test ESP32**:
   ```bash
   cd api
   python esp32_controller.py
   ```

2. **Test WebSocket**:
   ```bash
   curl http://localhost:8000/ws/detections
   ```

3. **Test Camera**:
   ```bash
   curl http://localhost:8000/api/video_feed
   ```

4. **Test Detection**:
   - Point camera at plate
   - Check console for OCR output

### Check System Requirements

- **Python**: 3.8+
- **OpenCV**: Installed and working
- **EasyOCR**: Installed and working
- **FastAPI**: Latest version
- **Camera**: Accessible and permissions granted

### Restart Everything

When in doubt:
```bash
# 1. Stop backend (Ctrl+C)
# 2. Stop frontend (Ctrl+C)
# 3. Restart ESP32 (reset button)
# 4. Wait 5 seconds
# 5. Start backend
# 6. Start frontend
# 7. Test connection
```

---

## Getting Help

If issues persist:

1. **Check logs** - Console output shows detailed error messages
2. **Check API docs** - `http://localhost:8000/docs`
3. **Test endpoints individually** - Isolate the problem
4. **Check network** - Ensure all devices can communicate

### Useful Commands

```bash
# Check backend is running
curl http://localhost:8000/

# Check ESP32 status
curl http://localhost:8000/api/esp32/status

# Check processes
tasklist | findstr python.exe

# Check ports
netstat -ano | findstr :8000
```
