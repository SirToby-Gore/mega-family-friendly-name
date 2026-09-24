import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from protocol import ProtocolError, wrap, unwrap
import game
from game import GameState, GameData, new_game, energy_upgrade, water_upgrade, size_upgrade

import json

# inside game_loop:
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


async def game_loop(state: GameData) -> None:
    while True:
        while not clients:
            await asyncio.sleep(0.1)

        await asyncio.sleep(TICK_SECONDS)
        commands = pending.copy()
        pending.clear()
        results = state.step(commands)
        for result in results:
            await broadcast(wrap("command_result", result))
        await broadcast(snapshot_message())


@router.websocket("/ws")
async def ws_endpoint(ws: WebSocket) -> None:
    await ws.accept()
    clients.add(ws)
    # new/reconnecting clients catch up immediately
    await ws.send_text(snapshot_message())
    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg_type, payload = unwrap(raw)
                ans = state.data.receive(msg_type, payload)
                ws.send_text(json.dumps(ans))
            except ProtocolError:
                continue                     # ignore malformed messages
            if msg_type == "command":
                pending.append(payload)
    except WebSocketDisconnect:
        pass
    finally:
        clients.discard(ws)
