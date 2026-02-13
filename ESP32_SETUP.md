# ESP32 Integration Setup Guide

This guide will help you connect your ESP32 hardware controller to the Plate Recognition System.

## Hardware Requirements

- ESP32 Development Board
- Green LED + 220Ω resistor
- Red LED + 220Ω resistor
- Buzzer (active or passive)
- Breadboard and jumper wires

## Hardware Wiring

Connect the components to your ESP32:

| Component | ESP32 GPIO Pin |
|-----------|---------------|
| Green LED | GPIO 25 (+ resistor) |
| Red LED   | GPIO 26 (+ resistor) |
| Buzzer    | GPIO 27 |
| Ground    | GND (all components) |

## Step 1: Upload Code to ESP32

1. **Install Thonny IDE**: Download from https://thonny.org/
2. **Configure ESP32**:
   - Connect ESP32 to computer via USB
   - Open Thonny
   - Go to Tools → Options → Interpreter
   - Select "MicroPython (ESP32)"
   - Select the correct COM port

3. **Upload the Code**:
   - Open the ESP32 code file provided
   - Update WiFi credentials:
     ```python
     WIFI_SSID = "YOUR_WIFI_NAME"
     WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
     ```
   - Click "Run" → "Save to device" → Select "MicroPython device"
   - Save as `main.py`

4. **Find ESP32 IP Address**:
   - After upload, the ESP32 will connect to WiFi
   - Check the Thonny console output for the IP address
   - Example output: `ESP32 IP Address: 192.168.1.100`
   - **Write down this IP address!**

## Step 2: Configure Backend

1. **Update ESP32 IP Address**:

   Edit `api/esp32_controller.py`:
   ```python
   ESP32_IP = "192.168.1.100"  # Replace with your ESP32's actual IP
   ```

2. **Enable/Disable ESP32**:

   In `api/esp32_controller.py`:
   ```python
   ESP32_ENABLED = True  # Set to False to disable ESP32
   ```

3. **Install Required Package**:
   ```bash
   pip install requests
   ```

## Step 3: Test Connection

### Test from ESP32 Web Interface

1. Open browser and go to: `http://YOUR_ESP32_IP`
2. You should see a control panel
3. Test the buttons:
   - **Registered Vehicle** → Green LED + short beep
   - **Unregistered Vehicle** → Red LED + long beep
   - **Test All** → Test all components
   - **All Off** → Turn everything off

### Test from Python Backend

Run the test script:
```bash
cd api
python esp32_controller.py
```

This will:
1. Check ESP32 connection
2. Test registered vehicle response
3. Test unregistered vehicle response
4. Turn off all outputs

## Step 4: Start the System

1. **Start Backend**:
   ```bash
   uvicorn api.main:app --reload
   ```

2. **Verify Integration**:
   - Go to http://localhost:8000/docs
   - Look for "ESP32 Hardware" section
   - Test endpoints:
     - `GET /api/esp32/status` - Check connection
     - `POST /api/esp32/test` - Test all components

## How It Works

When a plate is detected:

1. **Registered Vehicle** (in database):
   - ✅ Green LED turns on
   - 🔔 Short beep (200ms)
   - 💾 Logs to database
   - 📡 Broadcasts via WebSocket
   - 📱 Triggers ESP32

2. **Unregistered Vehicle** (not in database):
   - ❌ Red LED turns on
   - 🔔 Long beep (1 second)
   - 💾 Logs to database
   - 📡 Broadcasts via WebSocket
   - 📱 Triggers ESP32

## API Endpoints

### Check ESP32 Status
```http
GET /api/esp32/status
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

### Update ESP32 Configuration
```http
POST /api/esp32/config
Content-Type: application/json

{
  "ip": "192.168.1.100",
  "enabled": true
}
```

### Manual Trigger - Registered Vehicle
```http
POST /api/esp32/trigger/registered
```

### Manual Trigger - Unregistered Vehicle
```http
POST /api/esp32/trigger/unregistered
```

### Test All Components
```http
POST /api/esp32/test
```

### Turn Off All
```http
POST /api/esp32/off
```

## Troubleshooting

### ESP32 Not Connecting

1. **Check WiFi credentials** in ESP32 code
2. **Verify ESP32 is on same network** as your computer
3. **Check IP address** hasn't changed (ESP32 gets IP via DHCP)
4. **Restart ESP32** by pressing reset button or unplugging/replugging

### Backend Can't Connect to ESP32

1. **Verify IP address** in `api/esp32_controller.py`
2. **Ping the ESP32**:
   ```bash
   ping 192.168.1.100
   ```
3. **Check firewall** - ensure port 80 is not blocked
4. **Check ESP32 is running** - access web interface at `http://ESP32_IP`

### No Response from LEDs/Buzzer

1. **Check wiring** - verify GPIO pins and ground connections
2. **Test components** using ESP32 web interface
3. **Check component orientation** - LEDs have polarity (long leg = positive)
4. **Verify resistors** - LEDs need 220Ω resistors

### Backend Shows "ESP32 request timeout"

1. **Increase timeout** in `api/esp32_controller.py`:
   ```python
   REQUEST_TIMEOUT = 5  # Increase from 2 to 5 seconds
   ```
2. **Check network latency** - WiFi might be slow

### WebSocket Issues After Restart

See the main troubleshooting section. The integration now includes proper cleanup.

## Advanced Configuration

### Use Different GPIO Pins

Edit the ESP32 code:
```python
GREEN_LED_PIN = 25  # Change to your pin
RED_LED_PIN = 26    # Change to your pin
BUZZER_PIN = 27     # Change to your pin
```

### Adjust Beep Duration

Edit the ESP32 code:
```python
# In registered_vehicle() function
time.sleep(0.2)  # Short beep duration (change to 0.3, 0.5, etc.)

# In unregistered_vehicle() function
time.sleep(1)    # Long beep duration (change to 1.5, 2, etc.)
```

### Adjust LED On-Time

Edit the ESP32 code:
```python
# In registered_vehicle() function
time.sleep(3)  # LED stays on for 3 seconds (change as needed)

# In unregistered_vehicle() function
time.sleep(5)  # LED stays on for 5 seconds (change as needed)
```

### Disable ESP32 Without Removing Code

Set in `api/esp32_controller.py`:
```python
ESP32_ENABLED = False
```

Or via API:
```bash
curl -X POST http://localhost:8000/api/esp32/config \
  -H "Content-Type: application/json" \
  -d '{"ip": "192.168.1.100", "enabled": false}'
```

## Example Usage with curl

```bash
# Check status
curl http://localhost:8000/api/esp32/status

# Test registered vehicle
curl -X POST http://localhost:8000/api/esp32/trigger/registered

# Test unregistered vehicle
curl -X POST http://localhost:8000/api/esp32/trigger/unregistered

# Test all components
curl -X POST http://localhost:8000/api/esp32/test

# Turn off all
curl -X POST http://localhost:8000/api/esp32/off
```

## Security Notes

- ESP32 web server has **NO authentication** - only use on trusted networks
- Do NOT expose ESP32 to the internet
- Consider adding password protection if needed

## Questions?

Check the logs:
- **ESP32 logs**: View in Thonny serial monitor
- **Backend logs**: Check terminal running uvicorn

The system will show:
- `📡 Sending request to ESP32: http://192.168.1.100/registered`
- `✅ ESP32 response: GREEN LED ON + SHORT BEEP`
