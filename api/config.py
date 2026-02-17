import os

# =============================================================================
# HARDWARE CONFIGURATION
# =============================================================================

# Camera Source
# 0 for default laptop camera
# 1, 2, etc. for external USB cameras
# "rtsp://username:password@ip_address:554/stream" for IP cameras
CAMERA_SOURCE = 0

# =============================================================================
# ESP32 CONFIGURATION
# =============================================================================

# IP Address of the ESP32 Controller
ESP32_IP = "192.168.18.37"
ESP32_PORT = 80
ESP32_ENABLED = True

# =============================================================================
# API CONFIGURATION
# =============================================================================

# IP Address of the machine running the backend (FastAPI)
# standard loopback is "127.0.0.1"
# For external access, use the machine's LAN IP (e.g., "192.168.1.100")
API_HOST = "127.0.0.1"
API_PORT = 8000

# =============================================================================
# DETECTION SETTINGS
# =============================================================================

# Minimum confidence score (0.0 to 1.0) for a detection to be considered valid
CONFIDENCE_THRESHOLD = 0.60

# Number of times a plate must be seen in the buffer to be confirmed
VERIFICATION_COUNT = 3

# Number of frames to keep in buffer for temporal verification
BUFFER_SIZE = 5



# Seconds before the same plate can be re-logged
COOLDOWN_SECONDS = 30

# Process OCR every Nth frame (Lower = Faster detection, Higher = Better performance)
OCR_FRAME_INTERVAL = 15

# Use GPU for EasyOCR? (True/False)
# Set to True only if you have an NVIDIA GPU with CUDA installed
USE_GPU = False
