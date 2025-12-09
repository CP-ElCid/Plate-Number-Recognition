from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.database import Base, engine
from api.routes import vehicles, logs, detect, esp32
from fastapi import WebSocket
from api.websocket_manager import manager
from api.auth import router as auth_router
from api.camera_stream import router as camera_router, release_camera
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    print("🚀 Server starting up...")
    yield
    # Shutdown
    print("🛑 Server shutting down...")

    # Close all WebSocket connections
    print("📡 Closing WebSocket connections...")
    for connection in manager.active_connections[:]:
        try:
            await connection.close()
        except Exception as e:
            print(f"Error closing WebSocket: {e}")
    manager.active_connections.clear()

    # Release camera if active
    print("🎥 Releasing camera...")
    release_camera()

    print("✅ Shutdown complete")


app = FastAPI(title="Plate Recognition System", lifespan=lifespan)



# Allow frontend access (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost",
        "http://127.0.0.1",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Register routes
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(vehicles.router, prefix="/api/vehicles", tags=["Vehicles"])
app.include_router(logs.router, prefix="/api/logs", tags=["Logs"])
app.include_router(detect.router, prefix="/api/detect", tags=["Detection"])
app.include_router(camera_router, prefix="/api", tags=["Camera"])
app.include_router(esp32.router, prefix="/api/esp32", tags=["ESP32 Hardware"])

@app.get("/")
def root():
    return {"message": "Plate Recognition API Running 🚀"}



@app.websocket("/ws/detections")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print(f"✅ WebSocket client connected. Total clients: {len(manager.active_connections)}")
    try:
        while True:
            await websocket.receive_text()  # Just keep alive
    except Exception as e:
        print(f"❌ WebSocket connection closed: {e}")
    finally:
        manager.disconnect(websocket)
        print(f"🔌 WebSocket client disconnected. Total clients: {len(manager.active_connections)}")
