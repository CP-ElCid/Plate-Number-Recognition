"""
Configuration file for Plate Recognition System
"""

# ESP32 Hardware Controller Settings
ESP32_ENABLED = True  # Set to False to disable ESP32 integration
ESP32_IP = "192.168.1.100"  # Update with your ESP32's actual IP address
ESP32_PORT = 80

# Camera Settings
CAMERA_SOURCE = 0  # 0 for default camera, 1 for external camera

# Detection Settings
OCR_PROCESS_EVERY_N_FRAMES = 30  # Process OCR every N frames
PLATE_MIN_LENGTH = 5  # Minimum plate number length
PLATE_MAX_LENGTH = 10  # Maximum plate number length

# Database
DATABASE_URL = "sqlite:///./plate_system.db"
