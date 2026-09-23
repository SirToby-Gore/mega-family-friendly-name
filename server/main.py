import asyncio
# import aiofiles
import websockets
from models.game import GameState
import sim
from api.protocol import ProtocolError, unwrap, wrap
from contextlib import asynccontextmanager
import random
import math
import models
import api
from enum import Enum
from enum import Enum
import rich_stdout
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api.ws import game_loop, router

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


class CardRarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class Card:
    def __init__(self, name: str, description: str, rarity: CardRarity, sprite: str):
        self.name: str = name
        self.description: str = description
        self.rarity: CardRarity = rarity
        self.sprite: str = sprite

        def __str__(self):
            return f"{self.name}: {self.description} (Rarity: {self.rarity}, Sprite: {self.sprite})"


class ElectricCard(Card):
    def __init__(self, name: str, description: str, rarity: CardRarity, sprite: str):
        super().__init__(name, description, rarity, sprite)

    def __str__(self):
        return f"{super().__str__()})"


new_card = Card("Card Name", "Card Description",
                CardRarity.COMMON, "card_sprite.png")


class GameData:
    def __init__(self):
        self.day: int = 0
        self.money: float = 1000.0
        self.water: float = 100.0
        self.energy: float = 100.0
        self.requests: float = 1.0
        self.population_satisfaction: float = 100.0
        self.energy_generation_rate: float = 1.0
        self.water_consumption_rate: float = 1.0
        self.water_collection_rate: float = 1.0
        self.power_reliability: float = 1.0
        self.size: int = 1
        self.emissions: float = 0.0
        self.defeat: bool = False

    async def update(self) -> list[dict]:
        self.day += 1
        self.money += math.floor(self.requests * 1.1)
        self.requests *= 1.01
        self.energy += self.energy_generation_rate - self.energy_consumption_rate
        self.water += self.water_collection_rate - \
            self.water_consumption_rate - self.emissions
        self.population_satisfaction += self.requests - \
            self.emissions - self.water_consumption_rate - self.size
        self.energy_consumption_rate += self.requests
        self.water_consumption_rate += self.requests
        self.power_reliability -= self.energy_consumption_rate * 1.01

        data: dict = {
            "day": self.day,
            "money": self.money,
            "water": self.water,
            "energy": self.energy,
            "requests": self.requests,
            "population_satisfaction": self.population_satisfaction,
            "energy_generation_rate": self.energy_generation_rate,
            "water_consumption_rate": self.water_consumption_rate,
            "water_collection_rate": self.water_collection_rate,
            "power_reliability": self.power_reliability,
            "size": self.size,
            "emissions": self.emissions,
            "defeat": self.defeat
        }

        return [data]

    async def game_loop(self):
        while True:
            await self.update()
            await asyncio.sleep(1)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app",
                host="127.0.0.1", port=8000, reload=True)
