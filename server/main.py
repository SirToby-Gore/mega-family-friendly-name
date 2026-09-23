import asyncio
# import aiofiles
import asyncio
import websockets
from models.game import GameState
import sim
from api.protocol import ProtocolError, unwrap, wrap
import random
import math
import models
import api
from enum import Enum
from contextlib import asynccontextmanager
from enum import Enum

from fastapi import FastAPI

from api.ws import game_loop, router


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(game_loop(GameData()))   # start ticking when the server starts
    yield
    task.cancel()                             # stop ticking on shutdown


app = FastAPI(lifespan=lifespan)
app.include_router(router)


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
        self.water += self.water_collection_rate - self.water_consumption_rate - self.emissions
        self.population_satisfaction += self.requests - self.emissions - self.water_consumption_rate - self.size
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

        return [wrap("command", data)]


    async def game_loop(self):
        while True:
            await self.update()
            await asyncio.sleep(1)







'''    def step(state: GameState, commands: list[dict]) -> tuple[GameState, list[dict]]:
    """results = [
        {"id": cmd.get("id"), "ok": False, "reason": "UNKNOWN_COMMAND"}
        for cmd in commands
    ]

    new_state = replace(
        state,
        tick=state.tick + 1,
        money=state.money + INCOME_PER_TICK,
    )
    return new_state, results"""

    return state, state.update()'''