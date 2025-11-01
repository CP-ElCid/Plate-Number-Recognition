from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.database import Base, engine
from api.routes import vehicles, logs, detect
from fastapi import WebSocket
from api.websocket_manager import manager
import json

app = FastAPI(title="Plate Recognition System")



# Allow frontend access (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Register routes
app.include_router(vehicles.router, prefix="/api/vehicles", tags=["Vehicles"])
app.include_router(logs.router, prefix="/api/logs", tags=["Logs"])
app.include_router(detect.router, prefix="/api/detect", tags=["Detection"])

@app.get("/")
def root():
    return {"message": "Plate Recognition API Running 🚀"}



@app.websocket("/ws/detections")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Just keep alive
    except Exception:
        pass
    finally:
        manager.disconnect(websocket)
