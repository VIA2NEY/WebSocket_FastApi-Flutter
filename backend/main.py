
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict
from fastapi.responses import HTMLResponse

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)

    async def send_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

manager = ConnectionManager()

html = """
<!DOCTYPE html>
<html>
<body>
    <button onclick="sendMessage()">Envoyer au mobile</button>
    <script>
        const ws = new WebSocket('ws://127.0.0.1:8000/ws/web-client');
        
        function sendMessage() {
            ws.send(JSON.stringify({
                target_id: "1",  // ID de l'utilisateur mobile
                message: "Hello from web!",
                data: {
                    // Vos données JSON ici
                }
            }));
        }
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_json()
            print(f"Message reçu: {data}")  # Log
            target_id = data.get("target_id")
            await manager.send_message(data, target_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)
