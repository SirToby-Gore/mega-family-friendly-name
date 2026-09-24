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
        self.level_cap = self.size*10
        self.emissions: float = 0.0
        self.defeat: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "day": self.day,
            "tick": self.tick,
            "money": self.money,
            "water": round(self.water,2),
            "energy": round(self.energy,2),
            "requests": round(self.requests,2),
            "population-satisfaction": round(self.population_satisfaction,2),
            "energy-generation-rate": round(self.energy_generation_rate,2),
            "energy-consumption-rate": round(self.energy_consumption_rate,2),
            "water-consumption-rate": round(self.water_consumption_rate,2),
            "water-collection-rate": round(self.water_collection_rate,2),
            "power-reliability": round(self.power_reliability,2),
            "size": self.size,
            "emissions": round(self.emissions),
            "defeat": self.defeat,
            "energy-generation-level": energy_upgrade.level,
            "water-collection-level": water_upgrade.level,
            "level-cap": self.level_cap
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
        self.energy += (self.energy_generation_rate - self.energy_consumption_rate)
        self.water += (self.water_collection_rate - self.water_consumption_rate - self.emissions)
        self.energy_consumption_rate += self.requests * 0.01
        self.water_consumption_rate += self.requests * 0.01
        self.power_reliability = max(0.0, self.power_reliability - (self.energy_consumption_rate * 0.01))

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


class Upgrade:
    def __init__(self, name: str, description: str, cost: int, effect: Callable[[GameData], None]):
        self.upgrade_name: str = name
        self.description: str = description
        self.upgrade_cost: int = cost
        self.upgrade_effect: Callable[[GameData], None] = effect
        self.level: int = 0

    def purchase(self, game_data: GameData) -> bool:
        global level_cap

        # Check if the player can afford the upgrade
        if game_data.money < self.upgrade_cost:
            return False

        # Check level cap for normal upgrades
        if self != size_upgrade and self.level >= level_cap:
            return False

        # Check if size can be upgraded
        if self == size_upgrade and (energy_upgrade.level < level_cap or water_upgrade.level < level_cap):
            return False

        # Remove the cost
        game_data.money -= self.upgrade_cost

        # Apply the upgrade
        self.upgrade_effect(game_data)
        self.level += 1
        return True


def increase_energy_generation(game_data: GameData) -> None:
    game_data.energy_generation_rate *= 1.05


def increase_water_collection(game_data: GameData) -> None:
    game_data.water_collection_rate *= 1.05


def increase_size(game_data: GameData) -> None:
    game_data.size += 1

energy_upgrade = Upgrade(name="Power Plant", description="Increases energy generation rate by 5%.", cost=5000, effect=increase_energy_generation)
water_upgrade = Upgrade(name="Water Collector", description="Increases water collection rate by 5%.", cost=5000, effect=increase_water_collection)
size_upgrade = Upgrade(name="Size", description="Increases the size of your settlement by 1.", cost=10000, effect=increase_size)


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