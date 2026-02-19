"""
ESP32 Hardware Controller Routes
API endpoints to control and test ESP32 hardware
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.esp32_controller import esp32

router = APIRouter()


class ESP32Config(BaseModel):
    """ESP32 configuration model"""
    ip: str
    enabled: bool = True


class ESP32Status(BaseModel):
    """ESP32 status response model"""
    enabled: bool
    ip: str
    port: int
    is_connected: bool


@router.get("/status", response_model=ESP32Status)
async def get_esp32_status():
    """Get ESP32 connection status"""
    is_connected = esp32.check_connection()
    return ESP32Status(
        enabled=esp32.enabled,
        ip=esp32.ip,
        port=esp32.port,
        is_connected=is_connected
    )


@router.post("/config")
async def update_esp32_config(config: ESP32Config):
    """Update ESP32 configuration (IP address and enable/disable)"""
    esp32.update_ip(config.ip)
    esp32.enabled = config.enabled
    return {
        "status": "success",
        "message": f"ESP32 config updated: IP={config.ip}, Enabled={config.enabled}"
    }


@router.post("/trigger/registered")
async def trigger_registered():
    """Manually trigger registered vehicle response (Green LED + short beep)"""
    if not esp32.enabled:
        raise HTTPException(status_code=400, detail="ESP32 is disabled")

    success, msg = await esp32.trigger_registered()
    if success:
        return {"status": "success", "message": "Registered vehicle triggered"}
    else:
        raise HTTPException(status_code=500, detail=f"Failed to trigger ESP32: {msg}")


@router.post("/trigger/unregistered")
async def trigger_unregistered():
    """Manually trigger unregistered vehicle response (Red LED + long beep)"""
    if not esp32.enabled:
        raise HTTPException(status_code=400, detail="ESP32 is disabled")

    success, msg = await esp32.trigger_unregistered()
    if success:
        return {"status": "success", "message": "Unregistered vehicle triggered"}
    else:
        raise HTTPException(status_code=500, detail=f"Failed to trigger ESP32: {msg}")


@router.post("/test")
async def test_esp32():
    """Test all ESP32 components (LEDs and buzzer)"""
    if not esp32.enabled:
        raise HTTPException(status_code=400, detail="ESP32 is disabled")

    success, msg = await esp32.test_all()
    if success:
        return {"status": "success", "message": "ESP32 test completed"}
    else:
        raise HTTPException(status_code=500, detail=f"Failed to test ESP32: {msg}")


@router.post("/off")
async def turn_off_esp32():
    """Turn off all ESP32 outputs (LEDs and buzzer)"""
    if not esp32.enabled:
        raise HTTPException(status_code=400, detail="ESP32 is disabled")

    success, msg = await esp32.turn_off()
    if success:
        return {"status": "success", "message": "ESP32 outputs turned off"}
    else:
        raise HTTPException(status_code=500, detail=f"Failed to turn off ESP32: {msg}")
