import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from protocol import wrap
import game
from game import GameState, GameData, new_game

import rich_stdout

import json

# inside game_loop:
TICK_SECONDS = 1

terminal = rich_stdout.Terminal()

router = APIRouter()

state: GameState = new_game()
pending: list[dict] = []          # commands waiting for the next tick
clients: set[WebSocket] = set()   # currently connected browser


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
        try:
            results = state.step(commands)
            terminal.table(results)
            for result in results:
                await broadcast(wrap("event", result))
            await broadcast(snapshot_message())
        except Exception as exc:
            terminal.error(f"Tick {state.tick} failed: {exc!r}")
            continue

        if state.defeat:
            terminal.info(f"Game over: {state.reason}")
            return


@router.websocket("/ws")
async def ws_endpoint(ws: WebSocket) -> None:
    await ws.accept()
    clients.add(ws)
    # new/reconnecting clients catch up immediately
    await ws.send_text(snapshot_message())
    try:
        while True:
            raw = await ws.receive_text()
            terminal.info(f'Received {raw=}')
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                terminal.info("Ignored message: not valid JSON")
                continue
            if not isinstance(data, dict) or not isinstance(data.get("type"), str):
                terminal.info("Ignored message: missing 'type'")
                continue
            data.setdefault("payload", {})

            try:
                if state.data == None:
                    continue
                status, details = state.data.receive(data)
            except (KeyError, TypeError) as exc:   # e.g. play-card sent without an id
                status, details = "error", [
                    {"status": {"message": f"Bad command: {exc}"}}]

            await ws.send_text(wrap("command_result", {
                "command": data["type"],
                "ok": status == "success",
                "message": details[0]["status"]["message"],
            }))
    except WebSocketDisconnect:
        pass
    finally:
        clients.discard(ws)
