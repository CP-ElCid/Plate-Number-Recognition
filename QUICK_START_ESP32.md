# ESP32 Quick Start Guide

## 🚀 Quick Setup (5 Steps)

### 1. Upload to ESP32
- Open your ESP32 code in Thonny
- Update WiFi credentials:
  ```python
  WIFI_SSID = "YOUR_WIFI_NAME"
  WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
  ```
- Save to ESP32 as `main.py`
- **Note the IP address** shown in console (e.g., `192.168.1.100`)

### 2. Update Backend Config
Edit `api/esp32_controller.py`:
```python
ESP32_IP = "192.168.1.100"  # Your ESP32's IP
ESP32_ENABLED = True
```

### 3. Install Dependencies
```bash
pip install requests
```

### 4. Test Connection
```bash
cd api
python esp32_controller.py
```

### 5. Start Backend
```bash
uvicorn api.main:app --reload
```

## ✅ Verify It Works

1. Open browser: `http://localhost:8000/docs`
2. Find "ESP32 Hardware" section
3. Try `POST /api/esp32/test`
4. All LEDs and buzzer should activate

## 🔧 Hardware Wiring

| Component | GPIO Pin |
|-----------|----------|
| Green LED | 25       |
| Red LED   | 26       |
| Buzzer    | 27       |

Don't forget 220Ω resistors for LEDs!

## 📝 How It Works Automatically

When camera detects a plate:
- **Registered** → 🟢 Green LED + short beep
- **Unregistered** → 🔴 Red LED + long beep

## 🛠️ Manual Testing Endpoints

```bash
# Check status
curl http://localhost:8000/api/esp32/status

# Trigger green (registered)
curl -X POST http://localhost:8000/api/esp32/trigger/registered

# Trigger red (unregistered)
curl -X POST http://localhost:8000/api/esp32/trigger/unregistered

# Test all
curl -X POST http://localhost:8000/api/esp32/test

# Turn off
curl -X POST http://localhost:8000/api/esp32/off
```

## 🐛 Common Issues

**ESP32 won't connect?**
- Check WiFi credentials
- Ensure same network as your computer
- Try resetting ESP32

**Backend can't reach ESP32?**
- Verify IP in `esp32_controller.py` matches ESP32's IP
- Ping the ESP32: `ping 192.168.1.100`
- Check ESP32 web interface: `http://192.168.1.100`

**No LED/buzzer response?**
- Check wiring (GPIO pins + ground)
- Verify LED polarity (long leg = positive)
- Test via ESP32 web interface

## 📚 Full Documentation

See [ESP32_SETUP.md](ESP32_SETUP.md) for detailed guide.
