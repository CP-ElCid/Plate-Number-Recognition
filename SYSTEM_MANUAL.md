# Plate Number Recognition System - Complete Manual

## Table of Contents
1. [System Overview](#system-overview)
2. [System Architecture](#system-architecture)
3. [Hardware Requirements](#hardware-requirements)
4. [Software Requirements](#software-requirements)
5. [Installation Guide for New Laptop/Device](#installation-guide-for-new-laptopdevice)
6. [ESP32 Hardware Setup](#esp32-hardware-setup)
7. [System Configuration](#system-configuration)
8. [Running the System](#running-the-system)
9. [User Guide](#user-guide)
10. [API Reference](#api-reference)
11. [Troubleshooting](#troubleshooting)
12. [Maintenance & Updates](#maintenance--updates)

---

## System Overview

The **Plate Number Recognition System** is a comprehensive vehicle license plate detection and management system that combines:
- **Computer Vision** (OpenCV + EasyOCR) for real-time plate detection
- **Web Application** (React + FastAPI) for management and monitoring
- **Hardware Integration** (ESP32 microcontroller) for physical alerts (LEDs & buzzer)
- **Real-time Updates** (WebSocket) for instant notifications

### Key Features
- ✅ Real-time license plate detection from camera feed
- ✅ Vehicle registration management
- ✅ Detection logging and history tracking
- ✅ Physical hardware alerts (Green/Red LEDs + Buzzer)
- ✅ Real-time dashboard with WebSocket updates
- ✅ User authentication (JWT-based)
- ✅ Analytics and reporting
- ✅ Philippine timezone support

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                         │
│  - Dashboard (Real-time detection display)                  │
│  - Vehicle Management                                       │
│  - Detection Logs                                           │
│  - Reports & Analytics                                      │
│  Port: 5173                                                 │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTP/WebSocket
┌──────────────────▼──────────────────────────────────────────┐
│                    BACKEND (FastAPI)                        │
│  - Authentication (JWT)                                     │
│  - Camera Streaming & OCR Processing                        │
│  - Database Management (SQLite)                             │
│  - ESP32 Controller                                         │
│  - WebSocket Manager                                        │
│  Port: 8000                                                 │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTP Requests
┌──────────────────▼──────────────────────────────────────────┐
│                 ESP32 MICROCONTROLLER                       │
│  - WiFi Connected                                           │
│  - GPIO Control (LEDs + Buzzer)                             │
│  - HTTP Server                                              │
│  Port: 80                                                   │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│              PHYSICAL HARDWARE                              │
│  - Green LED (Registered Vehicle)                           │
│  - Red LED (Unregistered Vehicle)                           │
│  - Buzzer (Audio Alert)                                     │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Frontend:**
- React 19.1.1 (UI Framework)
- TypeScript 5.9.3
- Vite 7.1.7 (Build tool)
- Tailwind CSS 3.4.18 (Styling)
- Axios 1.13.1 (HTTP client)
- React Router 7.9.5 (Routing)

**Backend:**
- Python 3.x
- FastAPI 0.49.1+ (Web framework)
- Uvicorn 0.38.0+ (ASGI server)
- SQLAlchemy (ORM)
- EasyOCR (Plate recognition)
- OpenCV (Camera processing)
- SQLite (Database)

**Hardware:**
- ESP32 Development Board
- MicroPython firmware

---

## Hardware Requirements

### For the Computer/Laptop

**Minimum Requirements:**
- **OS**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Processor**: Intel Core i3 or equivalent (dual-core 2.0 GHz+)
- **RAM**: 4 GB minimum, 8 GB recommended
- **Storage**: 2 GB free space
- **Camera**: Built-in webcam or USB camera
- **Network**: WiFi or Ethernet for ESP32 communication

**Recommended Requirements:**
- **Processor**: Intel Core i5 or higher (quad-core 2.5 GHz+)
- **RAM**: 8 GB or more
- **Storage**: 5 GB free space (SSD preferred)
- **Camera**: 720p or higher resolution
- **GPU**: Dedicated GPU for faster OCR processing (optional)

### For ESP32 Hardware

**Required Components:**
- 1x ESP32 Development Board (ESP32-WROOM-32 or similar)
- 1x Green LED (5mm)
- 1x Red LED (5mm)
- 1x Buzzer (Active or Passive, 5V)
- Jumper wires (Male-to-Male)
- 1x  USB cable (for programming and power)
- Enclosure/case for ESP32 and components

---

## Software Requirements

### Required Software to Download

#### 1. **Python** (Version 3.8 to 3.11)
- **Download**: https://www.python.org/downloads/
- **Installation Notes**:
  - ✅ Check "Add Python to PATH" during installation
  - Verify installation: `python --version`

#### 2. **Node.js** (Version 18.x or higher)
- **Download**: https://nodejs.org/
- **Installation Notes**:
  - Install LTS version
  - Includes npm (Node Package Manager)
  - Verify installation: `node --version` and `npm --version`

#### 3. **Git** (Optional but recommended)
- **Download**: https://git-scm.com/downloads
- **Purpose**: Version control and cloning repository

#### 4. **Thonny IDE** (For ESP32 programming)
- **Download**: https://thonny.org/
- **Purpose**: Upload MicroPython code to ESP32
- **Alternative**: uPyCraft, Mu Editor, or esptool.py

#### 5. **Code Editor** (Optional)
- **VS Code**: https://code.visualstudio.com/ (Recommended)
- **Alternatives**: Sublime Text, Atom, Notepad++

---

## Installation Guide for New Laptop/Device

This section covers transferring the entire system to a new laptop or setting it up from scratch.

### Step 1: Install Required Software

1. **Install Python 3.8-3.11**
   ```bash
   # Verify installation
   python --version
   # or on some systems
   python3 --version
   ```

2. **Install Node.js 18+**
   ```bash
   # Verify installation
   node --version
   npm --version
   ```

3. **Install Thonny IDE** (for ESP32 setup)
   - Download from https://thonny.org/
   - Install using default settings

### Step 2: Transfer Project Files

**Option A: Using Git (Recommended)**
```bash
# If project is on GitHub/GitLab
git clone <repository-url>
cd Plate-Number-Recognition
```

**Option B: Manual Transfer**
1. Copy the entire `Plate-Number-Recognition` folder to new laptop
2. Transfer via USB drive, cloud storage, or network share
3. Ensure all files and folders are copied:
   ```
   Plate-Number-Recognition/
   ├── api/              (Backend files)
   ├── web/              (Frontend files)
   ├── Esp32/            (ESP32 code)
   ├── plate_system.db   (Database - optional)
   └── *.md files        (Documentation)
   ```

### Step 3: Install Python Dependencies

```bash
# Navigate to project folder
cd Plate-Number-Recognition

# Install backend dependencies
pip install fastapi uvicorn sqlalchemy easyocr opencv-python python-jose bcrypt requests pytz python-multipart
```

**If you encounter errors:**
```bash
# Try with pip3
pip3 install fastapi uvicorn sqlalchemy easyocr opencv-python python-jose bcrypt requests pytz python-multipart

# Or create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Then install packages
pip install fastapi uvicorn sqlalchemy easyocr opencv-python python-jose bcrypt requests pytz python-multipart
```

**Expected Installation Time**: 5-15 minutes (EasyOCR downloads large language models)

### Step 4: Install Frontend Dependencies

```bash
# Navigate to web folder
cd web

# Install Node.js packages
npm install
```

**Expected Installation Time**: 2-5 minutes

**If you encounter errors:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json  # On macOS/Linux
# or
rmdir /s node_modules & del package-lock.json  # On Windows

npm install
```

### Step 5: Configure Camera

1. **Identify your camera device**
   ```python
   # Test camera (create test_camera.py)
   import cv2

   # Try camera 0
   cap = cv2.VideoCapture(0)
   if cap.isOpened():
       print("Camera 0 works!")
   else:
       print("Try camera 1 or 2")
   ```

2. **Update camera source** in `api/config.py`:
   ```python
   CAMERA_SOURCE = 0  # 0 = default camera, 1 = external USB camera
   ```

### Step 6: Configure ESP32 IP Address

**After ESP32 setup (see next section):**

1. Note the ESP32 IP address from Thonny console
2. Update `api/config.py`:
   ```python
   ESP32_IP = "192.168.1.100"  # Replace with your ESP32's IP
   ESP32_ENABLED = True
   ```

### Step 7: Database Setup

The database will auto-create on first run. To start fresh:

```bash
# Delete existing database (optional)
rm plate_system.db  # macOS/Linux
del plate_system.db  # Windows

# Database will be recreated automatically when backend starts
```

### Step 8: Test Installation

**Test Backend:**
```bash
# From project root
uvicorn api.main:app --reload

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Test Frontend:**
```bash
# From web folder
cd web
npm run dev

# You should see:
# VITE ready in X ms
# ➜ Local: http://localhost:5173/
```

**Access the application:**
- Frontend: http://localhost:5173
- Backend API Docs: http://localhost:8000/docs
- Default Login: `admin` / `admin123`

---

## ESP32 Hardware Setup

### Understanding the ESP32 Code

The ESP32 runs **MicroPython** firmware and acts as a WiFi-connected hardware controller. Located in [`Esp32/boot.py`](Esp32/boot.py), it provides:

**Key Features:**
- **WiFi Setup Portal**: Access Point mode for easy WiFi configuration
- **Auto-Connect**: Saves WiFi credentials and auto-connects on boot
- **HTTP Server**: Receives commands from backend API
- **GPIO Control**: Controls LEDs and buzzer based on detection status

**GPIO Pin Configuration:**
- **GPIO 25**: Green LED (Registered vehicle)
- **GPIO 26**: Red LED (Unregistered vehicle)
- **GPIO 27**: Buzzer (Audio alert)

**Available Endpoints:**
- `GET /registered` - Trigger green LED + short beep (200ms)
- `GET /unregistered` - Trigger red LED + long beep (1 second)
- `GET /test` - Test all components sequentially
- `GET /off` - Turn off all outputs

### Step 1: Prepare ESP32 Hardware

**Wiring Diagram:**
```
ESP32 Board                Components
──────────────────────────────────────────────
GPIO 25 ──┬── [220Ω] ─── Green LED (+) ─── GND
          │
GPIO 26 ──┼── [220Ω] ─── Red LED (+)   ─── GND
          │
GPIO 27 ──┼───────────── Buzzer (+)    ─── GND
          │
GND ──────┴──────────────────────────────────
```

**LED Polarity (Important!):**
- Long leg = Positive (connects to resistor)
- Short leg = Negative (connects to GND)

**Breadboard Layout Example:**
```
Row 1: ESP32 GPIO25 → 220Ω Resistor → Green LED (+)
Row 2: ESP32 GPIO26 → 220Ω Resistor → Red LED (+)
Row 3: ESP32 GPIO27 → Buzzer (+)
Row 4: ESP32 GND → All component GND connections
```

### Step 2: Install MicroPython Firmware (First Time Only)

**Note:** Most ESP32 boards come with MicroPython pre-installed. Skip this if Thonny detects MicroPython.

1. **Download Firmware**:
   - Visit: https://micropython.org/download/esp32/
   - Download: `esp32-xxxxxx.bin` (latest stable)

2. **Flash Firmware** (using esptool):
   ```bash
   pip install esptool

   # Erase flash
   esptool.py --port COM3 erase_flash  # Windows (replace COM3 with your port)
   esptool.py --port /dev/ttyUSB0 erase_flash  # Linux
   esptool.py --port /dev/cu.usbserial-XXXX erase_flash  # macOS

   # Flash firmware
   esptool.py --chip esp32 --port COM3 write_flash -z 0x1000 esp32-xxxxx.bin
   ```

### Step 3: Upload Code to ESP32

1. **Open Thonny IDE**

2. **Configure Interpreter**:
   - Click: `Tools → Options → Interpreter`
   - Select: `MicroPython (ESP32)`
   - Port: Select your ESP32's COM port
     - Windows: `COM3`, `COM4`, etc.
     - macOS: `/dev/cu.usbserial-XXXX`
     - Linux: `/dev/ttyUSB0`
   - Click **OK**

3. **Connect ESP32**:
   - Plug ESP32 into computer via USB cable
   - Click **Stop/Restart** button in Thonny
   - You should see `>>>` prompt in Shell

4. **Upload boot.py**:
   - Open `Esp32/boot.py` in Thonny
   - Click **File → Save As...**
   - Select **MicroPython device**
   - Save as: `boot.py`
   - Wait for upload to complete

5. **Restart ESP32**:
   - Click **Stop/Restart** button
   - Watch the Shell output

### Step 4: Configure WiFi

**First Boot (No WiFi Configured):**

The ESP32 will enter **Access Point (AP) Mode** for setup:

1. **Connect to ESP32 WiFi**:
   - SSID: `ESP32_Config`
   - Password: `12345678`

2. **Open Web Browser**:
   - Navigate to: `http://192.168.4.1`

3. **Enter WiFi Credentials**:
   - WiFi SSID: Your network name
   - Password: Your WiFi password
   - Click **Save & Reboot**

4. **ESP32 Reboots and Connects**:
   - Watch Thonny Shell for connection status
   - Note the IP address displayed:
     ```
     Connected: ('192.168.1.100', '255.255.255.0', '192.168.1.1', '192.168.1.1')
     Main server running at: 192.168.1.100
     ```
   - **Write down this IP address!**

**Subsequent Boots:**
- ESP32 automatically connects to saved WiFi
- Retrieves IP via DHCP
- Starts HTTP server on port 80

**To Change WiFi:**
- Delete `wifi_config.txt` from ESP32 (via Thonny file browser)
- Restart ESP32 to enter AP mode again

### Step 5: Test ESP32 Hardware

**Method 1: Using Web Browser**

Open: `http://YOUR_ESP32_IP/test`
- All LEDs should light up sequentially
- Buzzer should beep

Test individual endpoints:
- `http://YOUR_ESP32_IP/registered` - Green LED + short beep
- `http://YOUR_ESP32_IP/unregistered` - Red LED + long beep
- `http://YOUR_ESP32_IP/off` - Turn everything off

**Method 2: Using curl/PowerShell**

```bash
# Test all components
curl http://192.168.1.100/test

# Test registered vehicle
curl http://192.168.1.100/registered

# Test unregistered vehicle
curl http://192.168.1.100/unregistered

# Turn off
curl http://192.168.1.100/off
```

**Expected Behavior:**

| Endpoint | Green LED | Red LED | Buzzer | Duration |
|----------|-----------|---------|--------|----------|
| /registered | ON | OFF | 200ms beep | 3 seconds |
| /unregistered | OFF | ON | 1 second beep | 5 seconds |
| /test | Blinks | Blinks | Short beep | Sequential |
| /off | OFF | OFF | OFF | Immediate |

### Step 6: Troubleshooting ESP32

**ESP32 won't connect to WiFi:**
- Verify WiFi credentials (case-sensitive)
- ESP32 only supports 2.4GHz WiFi (not 5GHz)
- Check router settings (WPA2/WPA3)
- Try moving ESP32 closer to router

**Can't find ESP32 IP address:**
- Check router's DHCP client list
- Use network scanner (Angry IP Scanner, Fing app)
- Reconnect to ESP32 AP and reconfigure

**Components not working:**
- Verify wiring connections
- Check LED polarity (long leg = +)
- Test with multimeter
- Replace faulty components
- Verify GPIO pins not damaged

**Thonny can't connect:**
- Check USB cable (use data cable, not charge-only)
- Install CH340/CP2102 drivers if needed
- Try different USB port
- Reset ESP32 by pressing reset button

---

## System Configuration

### Backend Configuration

**File**: `api/config.py`

```python
# ESP32 Hardware Controller Settings
ESP32_ENABLED = True                 # Set False to disable ESP32
ESP32_IP = "192.168.1.100"          # Your ESP32's IP address
ESP32_PORT = 80

# Camera Settings
CAMERA_SOURCE = 0                    # 0 = default, 1 = external USB cam

# Detection Settings
OCR_PROCESS_EVERY_N_FRAMES = 30     # Process every Nth frame
PLATE_MIN_LENGTH = 5                 # Minimum plate chars
PLATE_MAX_LENGTH = 10                # Maximum plate chars

# Database
DATABASE_URL = "sqlite:///./plate_system.db"

# Security (CHANGE IN PRODUCTION!)
SECRET_KEY = "SUPER_SECRET_KEY_CHANGE_THIS"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
```

**Important Configuration Notes:**

1. **ESP32_IP**: Must match your ESP32's actual IP
2. **CAMERA_SOURCE**:
   - `0` for built-in laptop camera
   - `1` for external USB camera
   - `2` for second external camera
3. **OCR_PROCESS_EVERY_N_FRAMES**:
   - Higher = better performance, less frequent detection
   - Lower = more frequent detection, higher CPU usage
4. **SECRET_KEY**: **MUST CHANGE FOR PRODUCTION!**
   - Generate: `openssl rand -hex 32`

### Frontend Configuration

**File**: `web/src/api/axiosClient.ts`

```typescript
const axiosClient = axios.create({
  baseURL: "http://127.0.0.1:8000/api",  // Backend API URL
  headers: {
    "Content-Type": "application/json",
  },
});
```

**For Network Access:**

If you want to access the frontend from other devices on your network:

**File**: `web/vite.config.ts`

```typescript
export default defineConfig({
  server: {
    host: '0.0.0.0',  // Expose to network
    port: 5173,
  },
})
```

Then access via: `http://YOUR_LAPTOP_IP:5173`

### Database Configuration

The system uses **SQLite** by default. For production with multiple users, consider PostgreSQL or MySQL.

**Tables Created Automatically:**

**Vehicles Table:**
- `id` (Primary Key)
- `name` (Vehicle owner)
- `plate_number` (Unique)
- `purpose` (Optional)
- `profile_picture` (Optional)
- `date_registered` (Philippine timezone)

**Logs Table:**
- `id` (Primary Key)
- `plate_number`
- `timestamp` (Philippine timezone)
- `status` ("registered" or "unregistered")
- `vehicle_id` (Foreign Key)

---

## Running the System

### Complete Startup Sequence

**1. Start ESP32** (if not already running):
- Ensure ESP32 is powered on
- Verify green LED blinks on connection (from WiFi setup)
- Confirm HTTP server is running

**2. Start Backend Server**:

```bash
# Navigate to project root
cd Plate-Number-Recognition

# Activate virtual environment (if using one)
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Start backend
uvicorn api.main:app --reload

# Expected output:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete.
```

**Backend runs on**: `http://127.0.0.1:8000`
**API Documentation**: `http://127.0.0.1:8000/docs`

**3. Start Frontend Server** (in new terminal):

```bash
# Navigate to web folder
cd Plate-Number-Recognition/web

# Start frontend
npm run dev

# Expected output:
# VITE v7.1.7  ready in 500 ms
# ➜  Local:   http://localhost:5173/
```

**Frontend runs on**: `http://localhost:5173`

**4. Open Application**:

Open browser and navigate to: `http://localhost:5173`

**Default Login Credentials:**
- Username: `admin`
- Password: `admin123`

### Verification Checklist

✅ **Backend is running**: Check `http://127.0.0.1:8000/docs`
✅ **Frontend is running**: Check `http://localhost:5173`
✅ **ESP32 is connected**: Check ESP32 status in backend logs or via API
✅ **Camera is accessible**: Check camera feed on Dashboard
✅ **Database is initialized**: Check for `plate_system.db` file
✅ **WebSocket is working**: Watch for real-time updates on Dashboard

---

## User Guide

### 1. Login

Navigate to `http://localhost:5173/login`

- Enter username: `admin`
- Enter password: `admin123`
- Click **Login**

### 2. Dashboard

**Real-time Detection Display**

The Dashboard shows:
- **Live Camera Feed**: Real-time video with detection
- **Latest Detection**: Most recent plate detected
- **Vehicle Details**: Name, purpose, image (if registered)
- **Status Indicator**: Green (registered) or Red (unregistered)

**Camera Controls:**
- **Start Camera**: Begin video streaming
- **Stop Camera**: Stop video streaming

**Manual Plate Check:**
- Enter plate number manually
- Click **Check**
- See vehicle info without creating log entry

**WebSocket Status:**
- Connected: Green indicator
- Disconnected: Red indicator (auto-reconnects)

### 3. Vehicle Management

**View Registered Vehicles:**
- Navigate to **Vehicles** page
- See list of all registered vehicles
- Search and filter options

**Add New Vehicle:**
1. Click **Add Vehicle** button
2. Fill in form:
   - **Name**: Vehicle owner name
   - **Plate Number**: License plate (unique)
   - **Purpose**: Vehicle purpose (optional)
   - **Profile Picture**: Image URL (optional)
3. Click **Save**

**Edit Vehicle:**
1. Click **Edit** button on vehicle row
2. Update information
3. Click **Save Changes**

**Delete Vehicle:**
1. Click **Delete** button
2. Confirm deletion
3. Vehicle removed (logs remain)

### 4. Detection Logs

**View All Logs:**
- Navigate to **Logs** page
- See all detection events
- Sorted by newest first

**Log Information:**
- Plate Number
- Date & Time (Philippine timezone)
- Status (Registered/Unregistered)
- Vehicle Details (if registered)

**Clear Logs:**
- Click **Clear All Logs** button
- Confirm action
- All logs deleted (vehicles remain)

### 5. Reports & Analytics

**View Statistics:**
- Total vehicles registered
- Total detections
- Registered vs Unregistered ratio
- Time-based analytics

**Charts:**
- Detection frequency
- Registration status breakdown
- Daily/weekly trends

### 6. ESP32 Hardware Status

**Check Status** (via API docs):
1. Go to `http://127.0.0.1:8000/docs`
2. Find **ESP32 Hardware** section
3. Try `GET /api/esp32/status`
4. See connection status, IP, enabled state

**Manual Testing:**
- `POST /api/esp32/trigger/registered` - Test green LED
- `POST /api/esp32/trigger/unregistered` - Test red LED
- `POST /api/esp32/test` - Test all components
- `POST /api/esp32/off` - Turn off all

### 7. Detection Flow

**Automatic Detection:**
1. Camera captures frames
2. Every 30 frames: OCR processing
3. Plate number extracted
4. Database lookup
5. If **Registered**:
   - ✅ Green LED + short beep
   - Log created with vehicle info
   - Dashboard updates via WebSocket
6. If **Unregistered**:
   - ❌ Red LED + long beep
   - Log created as unregistered
   - Dashboard updates via WebSocket

**Manual Detection:**
1. Enter plate number on Dashboard
2. Click **Check**
3. See vehicle info (no log created)
4. Option to add to logs if needed

---

## API Reference

### Authentication

**Login**
```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLC...",
  "token_type": "bearer"
}
```

**Get Current User**
```http
GET /api/auth/me
Authorization: Bearer <token>
```

### Detection

**Upload Image for Detection**
```http
POST /api/detect/
Content-Type: multipart/form-data
Authorization: Bearer <token>

file: <image_file>
```

Response:
```json
{
  "plate_number": "ABC1234",
  "status": "registered",
  "vehicle": {
    "name": "John Doe",
    "plate_number": "ABC1234",
    "purpose": "Daily commute"
  },
  "timestamp": "2024-12-09T10:30:00+08:00"
}
```

**Manual Plate Check**
```http
POST /api/detect/manual
Content-Type: application/json
Authorization: Bearer <token>

{
  "plate_number": "ABC1234"
}
```

### Vehicles

**Get All Vehicles**
```http
GET /api/vehicles/
Authorization: Bearer <token>
```

**Add Vehicle**
```http
POST /api/vehicles/
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "John Doe",
  "plate_number": "ABC1234",
  "purpose": "Daily commute",
  "profile_picture": "http://example.com/image.jpg"
}
```

**Update Vehicle**
```http
PUT /api/vehicles/ABC1234
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "John Doe Updated",
  "purpose": "Weekend use"
}
```

**Delete Vehicle**
```http
DELETE /api/vehicles/ABC1234
Authorization: Bearer <token>
```

### Logs

**Get All Logs**
```http
GET /api/logs/
Authorization: Bearer <token>
```

**Clear All Logs**
```http
DELETE /api/logs/clear
Authorization: Bearer <token>
```

### ESP32

**Get ESP32 Status**
```http
GET /api/esp32/status
Authorization: Bearer <token>
```

Response:
```json
{
  "enabled": true,
  "ip": "192.168.1.100",
  "port": 80,
  "is_connected": true
}
```

**Trigger Registered Vehicle**
```http
POST /api/esp32/trigger/registered
Authorization: Bearer <token>
```

**Trigger Unregistered Vehicle**
```http
POST /api/esp32/trigger/unregistered
Authorization: Bearer <token>
```

**Test All Components**
```http
POST /api/esp32/test
Authorization: Bearer <token>
```

### WebSocket

**Connect to Detection Stream**
```javascript
const ws = new WebSocket('ws://127.0.0.1:8000/ws/detections');

ws.onmessage = (event) => {
  const detection = JSON.parse(event.data);
  console.log(detection);
  // {
  //   plate_number: "ABC1234",
  //   status: "registered",
  //   timestamp: "2024-12-09T10:30:00+08:00",
  //   vehicle: {...}
  // }
};
```

---

## Troubleshooting

### Common Issues

#### 1. Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
pip install fastapi uvicorn sqlalchemy easyocr opencv-python python-jose bcrypt requests pytz
```

**Error**: `Address already in use`

**Solution**:
```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :8000
kill -9 <PID>
```

#### 2. Frontend Won't Start

**Error**: `Cannot find module...`

**Solution**:
```bash
cd web
rm -rf node_modules package-lock.json
npm install
```

**Error**: `Port 5173 already in use`

**Solution**:
```bash
# Kill process or use different port
npm run dev -- --port 5174
```

#### 3. Camera Not Working

**Error**: Camera feed shows black screen or error

**Solutions**:
- Check camera permissions (allow browser/Python)
- Try different `CAMERA_SOURCE` (0, 1, 2)
- Ensure camera not used by another app
- Restart computer

**Test camera**:
```python
import cv2
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
if ret:
    cv2.imshow('Test', frame)
    cv2.waitKey(0)
```

#### 4. ESP32 Connection Issues

**Error**: `ESP32 request timeout`

**Solutions**:
1. Verify ESP32 IP address:
   ```bash
   ping 192.168.1.100
   ```
2. Check `api/config.py` has correct IP
3. Ensure ESP32 and laptop on same network
4. Restart ESP32
5. Check firewall settings

**Error**: ESP32 won't connect to WiFi

**Solutions**:
- ESP32 only supports 2.4GHz WiFi
- Check WiFi credentials
- Move closer to router
- Try WPA2 instead of WPA3

#### 5. OCR Not Detecting Plates

**Issues**:
- Poor lighting conditions
- Camera too far/close
- Plate too small in frame
- Blur or low resolution

**Solutions**:
- Improve lighting
- Adjust camera position
- Increase camera resolution
- Clean camera lens
- Adjust `OCR_PROCESS_EVERY_N_FRAMES`

#### 6. WebSocket Disconnects

**Error**: WebSocket keeps reconnecting

**Solutions**:
- Check backend is running
- Restart backend server
- Clear browser cache
- Check network connection

#### 7. Database Errors

**Error**: `database is locked`

**Solution**:
- Close all connections to database
- Restart backend
- Delete `.db-journal` file if exists

**Error**: Table doesn't exist

**Solution**:
```bash
# Delete database and let it recreate
rm plate_system.db
# Restart backend - tables will be created
```

### Performance Optimization

**Slow OCR Processing:**
```python
# In api/config.py
OCR_PROCESS_EVERY_N_FRAMES = 60  # Increase from 30
```

**High CPU Usage:**
- Lower camera resolution
- Increase `OCR_PROCESS_EVERY_N_FRAMES`
- Close other applications
- Use dedicated GPU (if available)

**Slow Frontend:**
- Clear browser cache
- Use production build:
  ```bash
  cd web
  npm run build
  # Serve with:
  npm run preview
  ```

---

## Maintenance & Updates

### Regular Maintenance

**Daily:**
- Check system logs for errors
- Verify ESP32 connection
- Test camera feed

**Weekly:**
- Backup database:
  ```bash
  cp plate_system.db plate_system_backup_$(date +%Y%m%d).db
  ```
- Clear old logs (optional)
- Check disk space

**Monthly:**
- Update dependencies:
  ```bash
  pip install --upgrade fastapi uvicorn sqlalchemy
  cd web && npm update
  ```
- Review detection accuracy
- Clean up old logs

### Backup & Restore

**Backup:**
```bash
# Backup database
cp plate_system.db backups/plate_system_$(date +%Y%m%d).db

# Backup entire project
tar -czf plate_recognition_backup.tar.gz Plate-Number-Recognition/
```

**Restore:**
```bash
# Restore database
cp backups/plate_system_20241209.db plate_system.db

# Restart backend
```

### Updating the System

**Update Backend:**
```bash
cd Plate-Number-Recognition
git pull  # If using git
pip install --upgrade -r requirements.txt
```

**Update Frontend:**
```bash
cd web
git pull
npm install
npm run build
```

**Update ESP32:**
1. Modify `Esp32/boot.py`
2. Open in Thonny
3. Save to MicroPython device as `boot.py`
4. Restart ESP32

### Security Best Practices

1. **Change Default Password:**
   - Edit `api/auth.py`
   - Change admin password hash

2. **Change SECRET_KEY:**
   ```bash
   # Generate new key
   openssl rand -hex 32
   # Update in api/config.py
   ```

3. **Enable HTTPS** (Production):
   - Use reverse proxy (Nginx, Apache)
   - Obtain SSL certificate (Let's Encrypt)

4. **Secure ESP32:**
   - Use on trusted network only
   - Add authentication to ESP32 endpoints
   - Change AP password

5. **Database Security:**
   - Use PostgreSQL/MySQL for production
   - Enable authentication
   - Regular backups

### Support & Documentation

**Project Files:**
- `ESP32_SETUP.md` - Detailed ESP32 setup
- `QUICK_START_ESP32.md` - Quick ESP32 guide
- `TROUBLESHOOTING.md` - Extended troubleshooting

**API Documentation:**
- Interactive: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

**Logs Location:**
- Backend: Terminal output
- Frontend: Browser console (F12)
- ESP32: Thonny serial monitor

---

## Appendix

### Keyboard Shortcuts

**Dashboard:**
- `Ctrl+R` - Refresh page
- `F12` - Open developer tools
- `Ctrl+Shift+I` - Open inspector

### File Structure Reference

```
Plate-Number-Recognition/
├── api/                          # Backend (FastAPI)
│   ├── main.py                   # Application entry
│   ├── config.py                 # Configuration
│   ├── models.py                 # Database models
│   ├── schemas.py                # Pydantic schemas
│   ├── database.py               # DB setup
│   ├── auth.py                   # Authentication
│   ├── camera_stream.py          # Camera & OCR
│   ├── esp32_controller.py       # ESP32 integration
│   ├── websocket_manager.py      # WebSocket handler
│   └── routes/                   # API endpoints
│       ├── detect.py
│       ├── esp32.py
│       ├── vehicles.py
│       └── logs.py
├── web/                          # Frontend (React)
│   ├── src/
│   │   ├── pages/                # Page components
│   │   ├── components/           # Reusable components
│   │   ├── api/                  # API client
│   │   └── utils/                # Utilities
│   ├── package.json              # Dependencies
│   └── vite.config.ts            # Build config
├── Esp32/
│   └── boot.py                   # ESP32 MicroPython code
├── plate_system.db               # SQLite database
├── SYSTEM_MANUAL.md              # This file
├── ESP32_SETUP.md                # ESP32 guide
└── TROUBLESHOOTING.md            # Troubleshooting guide
```

### Command Reference

**Backend:**
```bash
# Start server
uvicorn api.main:app --reload

# Start with custom host/port
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Production mode
uvicorn api.main:app --workers 4
```

**Frontend:**
```bash
# Development
npm run dev

# Production build
npm run build

# Preview production
npm run preview

# Lint
npm run lint
```

**Database:**
```bash
# Python shell
python
>>> from api.database import engine
>>> from api.models import Base, Vehicle
>>> Base.metadata.create_all(engine)
```

### Environment Variables (Optional)

Create `.env` file in project root:

```env
# Backend
DATABASE_URL=sqlite:///./plate_system.db
SECRET_KEY=your-secret-key-here
ESP32_IP=192.168.1.100
CAMERA_SOURCE=0

# Frontend (in web/.env)
VITE_API_URL=http://127.0.0.1:8000
```

---

## Conclusion

You now have a complete guide to:
- ✅ Installing all required software
- ✅ Setting up the system on a new laptop
- ✅ Configuring and programming the ESP32
- ✅ Running the entire system
- ✅ Managing vehicles and detection logs
- ✅ Troubleshooting common issues

**Need Help?**
- Review troubleshooting section
- Check API documentation at `/docs`
- Examine log files for errors
- Verify all connections and configurations

**System is Ready When:**
- Backend shows "Application startup complete"
- Frontend loads at localhost:5173
- ESP32 shows IP and "Main server running"
- Camera feed visible on dashboard
- Test detection works with registered vehicle

**Happy Monitoring!** 🚗📸
