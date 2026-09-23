from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    await ws.send_json({"type": "hello"})
    try:
        while True:
            msg = await ws.receive_json()
            await ws.send_json({"type": "echo", "got": msg})
    except WebSocketDisconnect:
        pass