"""WebSocket endpoint and the tick loop that pushes snapshots to clients."""
import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from api.protocol import ProtocolError, unwrap, wrap
from models.game import GameState, new_game
from sim.step import step

TICK_SECONDS = 1.0

router = APIRouter()

state: GameState = new_game()
pending: list[dict] = []          # commands waiting for the next tick
clients: set[WebSocket] = set()   # currently connected browsers


def snapshot_message() -> str:
    return wrap("snapshot", {"state": state.to_dict()})


async def broadcast(raw: str) -> None:
    for ws in list(clients):
        try:
            await ws.send_text(raw)
        except Exception:
            clients.discard(ws)   # a dead client must not stop the loop


async def game_loop() -> None:
    global state
    while True:
        await asyncio.sleep(TICK_SECONDS)
        commands = pending.copy()
        pending.clear()
        state, results = step(state, commands)
        for result in results:
            await broadcast(wrap("command_result", result))
        await broadcast(snapshot_message())


@router.websocket("/ws")
async def ws_endpoint(ws: WebSocket) -> None:
    await ws.accept()
    clients.add(ws)
    await ws.send_text(snapshot_message())   # new/reconnecting clients catch up immediately
    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg_type, payload = unwrap(raw)
            except ProtocolError:
                continue                     # ignore malformed messages
            if msg_type == "command":
                pending.append(payload)
    except WebSocketDisconnect:
        pass
    finally:
        clients.discard(ws)