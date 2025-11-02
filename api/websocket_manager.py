from typing import List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        print(f"📢 Broadcasting to {len(self.active_connections)} WebSocket client(s)")
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
                print(f"   ✅ Sent to client")
            except Exception as e:
                print(f"   ❌ Failed to send to client: {e}")
                disconnected.append(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

# Singleton instance
manager = ConnectionManager()
