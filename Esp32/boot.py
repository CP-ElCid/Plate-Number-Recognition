"""
ESP32 MicroPython Web Server + WiFi Setup Portal (AP Mode)
With LED + Buzzer indicators

Green LED: GPIO 25
Red LED: GPIO 26
Buzzer: GPIO 27
"""

import network
import socket
import machine
import time
import os
from machine import Pin

# ===== GPIO SETUP =====
GREEN_LED_PIN = 25
RED_LED_PIN = 26
BUZZER_PIN = 27

green_led = Pin(GREEN_LED_PIN, Pin.OUT)
red_led = Pin(RED_LED_PIN, Pin.OUT)
buzzer = Pin(BUZZER_PIN, Pin.OUT)

green_led.off()
red_led.off()
buzzer.off()

# ===== FILE FOR SAVED WIFI =====
WIFI_FILE = "wifi_config.txt"

# ====================================================================
#                  LED / BUZZER STATUS FUNCTIONS
# ====================================================================

def blink_red(times=10, speed=0.3):
    for _ in range(times):
        red_led.on()
        time.sleep(speed)
        red_led.off()
        time.sleep(speed)

def beep(duration=0.2):
    buzzer.on()
    time.sleep(duration)
    buzzer.off()

def fail_beep():
    buzzer.on()
    time.sleep(1)
    buzzer.off()

# ====================================================================
#                   WIFI CONFIG FILE FUNCTIONS
# ====================================================================

def save_wifi_config(ssid, password):
    with open(WIFI_FILE, "w") as f:
        f.write(ssid + "\n" + password)

def load_wifi_config():
    if WIFI_FILE in os.listdir():
        with open(WIFI_FILE, "r") as f:
            lines = f.read().split("\n")
            if len(lines) >= 2:
                return lines[0], lines[1]
    return None, None

# ====================================================================
#                   WIFI CONNECTION LOGIC
# ====================================================================

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    print(f"Connecting to WiFi: {ssid}")
    wlan.connect(ssid, password)

    timeout = 15
    while not wlan.isconnected() and timeout > 0:
        print("Connecting...")
        blink_red(1, 0.2)
        timeout -= 1

    if wlan.isconnected():
        green_led.on()
        beep(0.1)
        print("Connected:", wlan.ifconfig())
        return wlan.ifconfig()[0]

    print("Failed to connect.")
    fail_beep()
    return None

# ====================================================================
#             WIFI SETUP PORTAL (AP MODE FOR CONFIG)
# ====================================================================

def start_ap_mode():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid="ESP32_Config", password="12345678")

    print("AP Mode Enabled. Connect to ESP32_Config")
    print("Go to http://192.168.4.1")

    return ap

def serve_wifi_setup_page():
    html = """
    <html>
    <head><title>ESP32 WiFi Setup</title></head>
    <body style='font-family:Arial'>
        <h2>ESP32 WiFi Setup</h2>
        <form action="/save" method="get">
            <label>WiFi SSID:</label><br>
            <input name="ssid" /><br><br>
            <label>Password:</label><br>
            <input name="pass" type="password"/><br><br>
            <button type="submit">Save & Reboot</button>
        </form>
    </body>
    </html>
    """
    return html

# ====================================================================
#                WEB SERVER (FOR WIFI SETUP MODE)
# ====================================================================

def start_wifi_config_server():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(3)
    print("Setup server running at 192.168.4.1")

    while True:
        cl, addr = s.accept()
        request = cl.recv(1024).decode()

        if "GET /save" in request:
            try:
                params = request.split("GET /save?")[1].split(" ")[0]
                ssid = params.split("ssid=")[1].split("&")[0]
                password = params.split("pass=")[1]

                ssid = ssid.replace("%20", " ")
                password = password.replace("%20", " ")

                save_wifi_config(ssid, password)

                response = "Saved! Rebooting ESP32..."
                cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n" + response)
                cl.close()

                time.sleep(2)
                machine.reset()

            except:
                cl.send("HTTP/1.1 400 Bad Request\r\n\r\nError Saving Credentials")
                cl.close()

        else:
            cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" +
                    serve_wifi_setup_page())
            cl.close()

# ====================================================================
#              YOUR ORIGINAL DEVICE CONTROL FUNCTIONS
# ====================================================================

def registered_vehicle():
    green_led.on()
    red_led.off()
    beep(0.2)
    time.sleep(3)
    green_led.off()
    return "REGISTERED VEHICLE"

def unregistered_vehicle():
    red_led.on()
    green_led.off()
    # No buzzer for unregistered — only red LED
    time.sleep(5)
    red_led.off()
    return "UNREGISTERED VEHICLE"

def all_off():
    green_led.off()
    red_led.off()
    buzzer.off()
    return "ALL OFF"

def test_mode():
    green_led.on(); time.sleep(0.3); green_led.off()
    red_led.on(); time.sleep(0.3); red_led.off()
    beep(0.2)
    return "TEST OK"

# ====================================================================
#                   MAIN WEB SERVER (AFTER WIFI)
# ====================================================================

def handle_main_request(req):
    try:
        path = req.split(" ")[1]
    except:
        return "HTTP/1.1 400 ERROR\r\n\r\nBad Request"

    if path == "/registered":
        msg = registered_vehicle()
    elif path == "/unregistered":
        msg = unregistered_vehicle()
    elif path == "/test":
        msg = test_mode()
    elif path == "/off":
        msg = all_off()
    else:
        msg = "ESP32 Plate Recognition Controller"

    return "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n" + msg

def start_main_server(ip):
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(5)
    print("Main server running at:", ip)

    while True:
        cl, addr = s.accept()
        req = cl.recv(1024).decode()
        response = handle_main_request(req)
        cl.send(response)
        cl.close()

# ====================================================================
#                           MAIN PROGRAM
# ====================================================================

print("\nBooting ESP32...\n")

saved_ssid, saved_pass = load_wifi_config()

if saved_ssid:
    ip = connect_wifi(saved_ssid, saved_pass)

    if ip:
        start_main_server(ip)
    else:
        print("Switching to AP Config Mode...")
        start_ap_mode()
        start_wifi_config_server()

else:
    print("No WiFi credentials found!")
    blink_red(5)
    start_ap_mode()
    start_wifi_config_server()

