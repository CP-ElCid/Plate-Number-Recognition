from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.database import Base, engine
from api.routes import vehicles, logs, detect
from fastapi import WebSocket
from api.websocket_manager import manager
import json
from api.auth import router as auth_router
from api.camera_stream import router as camera_router



app = FastAPI(title="Plate Recognition System")



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
