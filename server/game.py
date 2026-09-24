from dataclasses import dataclass, asdict
from enum import Enum
import math
import random
from typing import Callable, Any

STATE_VERSION = 1


class CardRarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class Card:
    def __init__(self, name: str, description: str, rarity: CardRarity, sprite: str, effect: Callable[[Any], None]):
        self.name: str = name
        self.description: str = description
        self.rarity: CardRarity = rarity
        self.sprite: str = sprite
        self.effect: Callable[[Any], None] = effect

    def __str__(self) -> str:
        return f"{self.name}: {self.description} (Rarity: {self.rarity.value}, Sprite: {self.sprite})"

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


class GameData:
    def __init__(self, money: int = 100000) -> None:
        self.tick: int = 0
        self.day: int = 0
        self.money: int = money
        self.water: float = 100.0
        self.energy: float = 100.0
        self.requests: float = 1.0
        self.population_satisfaction: float = 100.0

        # Balance Rates
        self.energy_generation_rate: float = 1.0
        self.energy_consumption_rate: float = 0.5
        self.water_consumption_rate: float = 1.0
        self.water_collection_rate: float = 1.0
        self.power_reliability: float = 100.0
        self.size: int = 1
        self.emissions: float = 0.0
        self.defeat: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "tick": self.tick,
            "day": self.day,
            "money": self.money,
            "water": self.water,
            "energy": self.energy,
            "requests": self.requests,
            "population_satisfaction": self.population_satisfaction,
            "energy_generation_rate": self.energy_generation_rate,
            "energy_consumption_rate": self.energy_consumption_rate,
            "water_consumption_rate": self.water_consumption_rate,
            "water_collection_rate": self.water_collection_rate,
            "power_reliability": self.power_reliability,
            "size": self.size,
            "emissions": self.emissions,
            "defeat": self.defeat,
        }

    def step(self, commands: list[dict]) -> list[dict]:
        results = []

        # Process commands
        for cmd in commands:
            cmd_id = cmd.get("id")
            cmd_type = cmd.get("type")
            results.append({
                "id": cmd_id,
                "ok": False,
                "reason": f"UNKNOWN_COMMAND_{cmd_type}"
            })

        # Advance tick & day counters
        self.tick += 1
        if self.tick % 10 == 0:
            self.day += 1

        # Update resource values
        self.money += math.floor(self.requests * 110)
        self.requests *= 1.001
        self.energy += self.energy_generation_rate - self.energy_consumption_rate
        self.water += self.water_collection_rate - \
            self.water_consumption_rate - self.emissions
        self.energy_consumption_rate += self.requests * 0.01
        self.water_consumption_rate += self.requests * 0.01
        self.power_reliability = max(
            0.0, self.power_reliability - (self.energy_consumption_rate * 0.01))

        # Check loss condition
        if self.power_reliability <= 0 or self.water <= 0:
            self.defeat = True

        # Spawn cards periodically
        if self.day > 0 and self.day % 30 == 0 and self.tick % 10 == 0:
            card_rarity = Card.spawn()
            results.append({
                "event": "card_spawned",
                "rarity": card_rarity.value
            })

        return results


@dataclass
class GameState:
    version: int = STATE_VERSION
    data: GameData | None = None

    def __post_init__(self) -> None:
        if self.data is None:
            self.data = GameData()

    def to_dict(self) -> dict[str, Any]:
        if self.data == None:
            return {}

        return {
            "version": self.version,
            "state": self.data.to_dict()
        }


def new_game() -> GameState:
    return GameState(data=GameData(money=100000))
