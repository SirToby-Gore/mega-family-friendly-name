import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import api
import models
import rich_stdout
import sim
from api.protocol import ProtocolError, unwrap, wrap
from api.ws import game_loop, router
from models.game import GameData, GameState

terminal = rich_stdout.Terminal()


@asynccontextmanager
async def lifespan(app: FastAPI):
    host = "127.0.0.1"
    port = 8000
    print(f"\nServer running! WebSocket link: ws://{host}:{port}/ws\n")

    task = asyncio.create_task(game_loop(GameData()))
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)
app.include_router(router)

# Resolves BASE_DIR to the root 'src/' folder
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Mount static asset endpoints
app.mount(
    "/js",
    StaticFiles(directory=os.path.join(BASE_DIR, "client", "js")),
    name="js",
)
app.mount(
    "/css",
    StaticFiles(directory=os.path.join(BASE_DIR, "client", "css")),
    name="css",
)
app.mount(
    "/assets",
    StaticFiles(directory=os.path.join(BASE_DIR, "assets")),
    name="assets",
)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)


@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(BASE_DIR, "client", "index.html"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
