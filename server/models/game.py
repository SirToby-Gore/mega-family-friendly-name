from dataclasses import dataclass, asdict
import math
import asyncio
from typing import Any
from typing import Callable
from enum import Enum
import random


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
            card_rarity = Card.spawn()
            print(f"Spawned a {card_rarity.value} card!")
            data["spawned_card"] = card_rarity.value

        return [data]

    async def game_loop(self):
        while True:
            self.update()
            Card.spawn()
            await asyncio.sleep(1)


class CardRarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


def get_spawn_rate(rarity: CardRarity) -> int:
    match rarity:
        case CardRarity.COMMON:
            return 50
        case CardRarity.UNCOMMON:
            return 35
        case CardRarity.RARE:
            return 10
        case CardRarity.EPIC:
            return 4
        case CardRarity.LEGENDARY:
            return 1


class Card:
    def __init__(self, name: str, description: str, rarity: CardRarity, sprite: str, effect: Callable):
        self.name: str = name
        self.description: str = description
        self.rarity: CardRarity = rarity
        self.sprite: str = sprite
        self.effect: Callable = effect

    def __str__(self):
        return f"{self.name}: {self.description} (Rarity: {self.rarity}, Sprite: {self.sprite})"

    @staticmethod
    def spawn() -> CardRarity:
        random_number = random.randint(1, 100)

        if random_number <= 50:
            return CardRarity.COMMON
        elif random_number <= 85:
            return CardRarity.UNCOMMON
        elif random_number <= 95:
            return CardRarity.RARE
        elif random_number <= 99:
            return CardRarity.EPIC
        else:
            return CardRarity.LEGENDARY


"""new_card = Card("Card Name", "give ya 100 smackers", CardRarity.COMMON, "card_sprite.png", lambda state: state.money += 100)
new_card.effect(self)"""


def new_game() -> GameState:
    return GameState(money=1000)  # starting cash: 1,000.00
