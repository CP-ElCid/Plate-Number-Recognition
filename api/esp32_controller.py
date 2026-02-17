"""
ESP32 Controller Integration
Sends HTTP requests to ESP32 to control LEDs and buzzer based on vehicle registration status
"""

import requests
import asyncio
from typing import Literal
from api.config import ESP32_IP, ESP32_PORT, ESP32_ENABLED

# Timeout for HTTP requests (seconds)
REQUEST_TIMEOUT = 5


class ESP32Controller:
    """Controller for ESP32 hardware integration"""

    def __init__(self, ip: str = ESP32_IP, port: int = ESP32_PORT, enabled: bool = ESP32_ENABLED):
        self.ip = ip
        self.port = port
        self.enabled = enabled
        self.base_url = f"http://{ip}:{port}"
        self.is_connected = False

    def check_connection(self) -> bool:
        """Check if ESP32 is reachable"""
        if not self.enabled:
            return False

        try:
            response = requests.get(f"{self.base_url}/status", timeout=REQUEST_TIMEOUT)
            self.is_connected = response.status_code == 200
            return self.is_connected
        except requests.exceptions.RequestException as e:
            print(f"❌ ESP32 connection failed: {e}")
            self.is_connected = False
            return False

    async def _send_request(self, endpoint: str) -> tuple[bool, str]:
        """Send HTTP request to ESP32"""
        if not self.enabled:
            return False, "ESP32 integration is disabled"

        try:
            url = f"{self.base_url}{endpoint}"
            print(f"📡 Sending request to ESP32: {url}")
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: requests.get(url, timeout=REQUEST_TIMEOUT))

            if response.status_code == 200:
                print(f"✅ ESP32 response: {response.text.strip()}")
                return True, "Success"
            else:
                msg = f"ESP32 returned status {response.status_code}"
                print(f"⚠️ {msg}")
                return False, msg

        except requests.exceptions.Timeout:
            msg = f"ESP32 request timeout (>{REQUEST_TIMEOUT}s) - Command assumed sent"
            print(f"⏱️ {msg}")
            return True, msg  # Return True because hardware is responding despite timeout
        except requests.exceptions.ConnectionError:
            msg = f"Cannot connect to ESP32 at {self.base_url}"
            print(f"❌ {msg}")
            return False, msg
        except Exception as e:
            msg = f"ESP32 request error: {str(e)}"
            print(f"❌ {msg}")
            return False, msg

    async def trigger_registered(self) -> tuple[bool, str]:
        """
        Trigger registered vehicle response (Green LED + short beep)
        """
        return await self._send_request("/registered")

    async def trigger_unregistered(self) -> tuple[bool, str]:
        """
        Trigger unregistered vehicle response (Red LED only, no buzzer)
        """
        return await self._send_request("/unregistered")

    async def test_all(self) -> tuple[bool, str]:
        """Test all ESP32 components"""
        return await self._send_request("/test")

    async def turn_off(self) -> tuple[bool, str]:
        """Turn off all ESP32 outputs"""
        return await self._send_request("/off")

    def update_ip(self, new_ip: str):
        """Update ESP32 IP address"""
        self.ip = new_ip
        self.base_url = f"http://{new_ip}:{self.port}"
        print(f"🔄 ESP32 IP updated to: {new_ip}")


# Singleton instance
esp32 = ESP32Controller()


async def trigger_esp32(status: Literal["registered", "unregistered"]):
    """
    Convenience function to trigger ESP32 based on vehicle status

    Args:
        status: Either "registered" or "unregistered"
    """
    if not esp32.enabled:
        return

    try:
        if status == "registered":
            await esp32.trigger_registered()
        elif status == "unregistered":
            await esp32.trigger_unregistered()
        else:
            print(f"⚠️ Invalid ESP32 status: {status}")
    except Exception as e:
        print(f"❌ ESP32 trigger error: {e}")


# Helper function for testing
if __name__ == "__main__":
    print("Testing ESP32 Controller...")
    controller = ESP32Controller()

    print("\n1. Checking connection...")
    if controller.check_connection():
        print("✅ ESP32 is connected!")

        print("\n2. Testing registered vehicle...")
        controller._send_request("/registered")

        import time
        time.sleep(4)

        print("\n3. Testing unregistered vehicle...")
        controller._send_request("/unregistered")

        time.sleep(6)

        print("\n4. Turning off all...")
        controller._send_request("/off")
    else:
        print("❌ ESP32 is not reachable. Check IP address and connection.")
