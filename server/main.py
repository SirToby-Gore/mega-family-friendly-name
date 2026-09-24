import asyncio
# import aiofiles
import websockets
import api
from api.protocol import ProtocolError, unwrap, wrap
from api.ws import game_loop, router
import models
from models.game import GameState, GameData
import sim
import random
import math
import rich_stdout
import os

from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from contextlib import asynccontextmanager

terminal = rich_stdout.Terminal()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Print your WebSocket endpoint URL on startup
    host = "127.0.0.1"
    port = 8000
    print(f"\nServer running! WebSocket link: ws://{host}:{port}/ws\n")

    # Start ticking background task when server starts
    task = asyncio.create_task(game_loop(GameData()))

    yield

    # Stop ticking on shutdown
    task.cancel()

app = FastAPI(lifespan=lifespan)
app.include_router(router)

app = FastAPI(lifespan=lifespan)
app.include_router(router)

# Base directory setup
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Mount static asset folders
app.mount(
    "/js", StaticFiles(directory=os.path.join(BASE_DIR, "client", "js")), name="js")
app.mount("/css", StaticFiles(directory=os.path.join(BASE_DIR,
          "client", "css")), name="css")
app.mount(
    "/assets", StaticFiles(directory=os.path.join(BASE_DIR, "assets")), name="assets")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)  # No content


@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(BASE_DIR, "client", "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app",
                host="127.0.0.1", port=8000, reload=True)
