from dataclasses import dataclass, asdict
import math
import asyncio
from typing import Any
import card

STATE_VERSION = 1


@dataclass
class GameState:
    version: int = STATE_VERSION
    tick: int = 0
    money: int = 0

    def __init__(self, money: float) -> None:
        self.data: GameData = GameData(money)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        if data.get("version") != STATE_VERSION:
            raise ValueError(
                f"Unsupported save version: {data.get('version')}")
        return cls(**data)


class GameData:
    def __init__(self, money: float = 1000.0):
        self.day: int = 0
        self.money: float = money
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

    def update(self) -> list[dict]:
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

        if self.day % 30 == 0:
            card_rarity = card.Card.spawn()
            print(f"Spawned a {card_rarity.value} card!")
            data["spawned_card"] = card_rarity.value

        return [data]

    async def game_loop(self):
        while True:
            self.update()
            card.Card.spawn()
            await asyncio.sleep(1)


def new_game() -> GameState:
    return GameState(money=1000)  # starting cash: 1,000.00
