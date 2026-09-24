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
    LEGENDARY = "legendary"


class Card:
    def __init__(self, name: str, description: str, rarity: CardRarity, effect: Callable[[Any], None]):
        self.name: str = name
        self.description: str = description
        self.rarity: CardRarity = rarity
        self.effect: Callable[[GameData], None] = effect

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
        self.electricity_bills: float = 1.0
        self.energy_generation_rate: float = 1.0
        self.energy_consumption_rate: float = 0.5
        self.water_consumption_rate: float = 1.0
        self.water_collection_rate: float = 1.0
        self.power_reliability: float = 100.0
        self.size: int = 1
        self.level_cap = self.size*10
        self.emissions: float = 0.0
        self.defeat: bool = False
        self.energy_upgrade = Upgrade(name="Power Plant", description="Increases energy generation rate by 5%.",
                                      cost=5000, effect=increase_energy_generation)
        self.water_upgrade = Upgrade(name="Water Collector", description="Increases water collection rate by 5%.",
                                     cost=5000, effect=increase_water_collection)
        self.size_upgrade = Upgrade(name="Size", description="Increases the size of your settlement by 1.",
                                    cost=10000, effect=increase_size)

    def to_dict(self) -> dict[str, Any]:
        return {
            "day": self.day,
            "tick": self.tick,
            "money": self.money,
            "water": round(self.water, 2),
            "energy": round(self.energy, 2),
            "requests": round(self.requests, 2),
            "population-satisfaction": round(self.population_satisfaction, 2),
            "energy-generation-rate": round(self.energy_generation_rate, 2),
            "energy-consumption-rate": round(self.energy_consumption_rate, 2),
            "electricity-bills": round(self.electricity_bills, 2),
            "water-consumption-rate": round(self.water_consumption_rate, 2),
            "water-collection-rate": round(self.water_collection_rate, 2),
            "power-reliability": round(self.power_reliability, 2),
            "size": self.size,
            "emissions": round(self.emissions),
            "defeat": self.defeat,
            "energy-generation-level": self.energy_upgrade.level,
            "water-collection-level": self.water_upgrade.level,
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
        self.money += math.floor(self.requests * 110) - self.electricity_bills
        self.requests *= 1.001
        self.energy += (self.energy_generation_rate -
                        self.energy_consumption_rate)
        self.water += (self.water_collection_rate -
                       self.water_consumption_rate - self.emissions)
        self.energy_consumption_rate += self.requests * 0.01
        self.water_consumption_rate += self.requests * 0.01
        self.electricity_bills = self.energy_consumption_rate * 2
        self.power_reliability = max(
            0.0, self.power_reliability - (self.energy_consumption_rate * 0.01))

        # Check loss condition
        if self.power_reliability <= 0 or self.water <= 0:
            self.defeat = True

        # Spawn cards periodically
        if self.day > 0 and self.day % 5 == 0 and self.tick % 10 == 0:
            card_rarity = Card.spawn()
            results.append({
                "event": "card_spawned",
                "rarity": card_rarity.value
            })

        return results

    def receive(self, msg_type: str, payload: dict[str, any]) -> any:
        match msg_type:
            case 'buy-electric-upgrade':
                if self.money < self.energy_upgrade.upgrade_cost:
                    return {
                        'type': 'error',
                        'status': {
                            'message': 'not enough money to buy an energy upgrade'
                        }
                    }

                if self.level_cap <= self.energy_upgrade.level:
                    return {
                        'type': 'error',
                        'status': {
                            'message': 'level cap can not be exceeded'
                        }
                    }

                self.money -= self.energy_upgrade.upgrade_cost
                self.energy_upgrade.level += 1

                return {
                    'type': 'success',
                    'status': {
                        'message': f'upgraded energy to level {self.energy_upgrade.level}'
                    }
                }

            case 'buy-water-upgrade':
                if self.money < self.water_upgrade.upgrade_cost:
                    return {
                        'type': 'error',
                        'status': {
                            'message': 'not enough money to buy an water upgrade'
                        }
                    }

                if self.level_cap <= self.water_upgrade.level:
                    return {
                        'type': 'error',
                        'status': {
                            'message': 'level cap can not be exceeded'
                        }
                    }

                self.money -= self.water_upgrade.upgrade_cost
                self.water_upgrade.level += 1

                return {
                    'type': 'success',
                    'status': {
                        'message': f'upgraded water to level {self.water_upgrade.level}'
                    }
                }

            case 'buy-size-upgrade':
                if self.money < self.size_upgrade.upgrade_cost:
                    return {
                        'type': 'error',
                        'status': {
                            'message': 'not enough money to buy an size upgrade'
                        }
                    }

                self.money -= self.size_upgrade.upgrade_cost
                self.size_upgrade.level += 1
                self.level_cap += 3

                return {
                    'type': 'success',
                    'status': {
                        'message': f'upgraded energy to size {self.size_upgrade.level}',
                    }
                }

            case _:
                return {
                    'type': 'error',
                    'status': {
                        'message': f'no implemented method {msg_type}'
                    }
                }


class Upgrade:
    def __init__(self, name: str, description: str, cost: int, effect: Callable[[GameData], None]):
        self.upgrade_name: str = name
        self.description: str = description
        self.upgrade_cost: int = cost
        self.upgrade_effect: Callable[[GameData], None] = effect
        self.level: int = 0

# region cards


def increase_energy_generation(game_data: GameData) -> None:
    game_data.energy_generation_rate *= 1.05


def increase_water_collection(game_data: GameData) -> None:
    game_data.water_collection_rate *= 1.05


def increase_size(game_data: GameData) -> None:
    game_data.size += 1


# CARDS
def card1_effect(game_data: GameData) -> None:
    game_data.energy_generation_rate *= 1.12
    game_data.energy_consumption_rate *= 1.08
    game_data.power_reliability -= 4


def card2_effect(game_data: GameData) -> None:
    game_data.money *= 1.05
    game_data.energy_generation_rate *= 1.15
    game_data.power_reliability -= 14


def card3_effect(game_data: GameData) -> None:
    game_data.energy_generation_rate *= 1.10
    game_data.energy_consumption_rate *= 0.90
    game_data.power_reliability -= 8


def card4_effect(game_data: GameData) -> None:
    game_data.energy_generation_rate *= 1.10
    game_data.energy_consumption_rate *= 1.05
    game_data.requests *= 1.05


def card5_effect(game_data: GameData) -> None:
    game_data.money *= 1.08
    game_data.energy_consumption_rate *= 1.06
    game_data.requests *= 1.05


def card6_effect(game_data: GameData) -> None:
    game_data.energy_generation_rate *= 1.15
    game_data.power_reliability -= 6


def card7_effect(game_data: GameData) -> None:
    game_data.money *= 1.05
    game_data.power_reliability -= 4


def card8_effect(game_data: GameData) -> None:
    game_data.energy_consumption_rate *= 0.92
    game_data.money *= 0.97


def card9_effect(game_data: GameData) -> None:
    game_data.water_consumption_rate *= 0.90
    game_data.money *= 0.97
    game_data.population_satisfaction += 4


def card10_effect(game_data: GameData) -> None:
    game_data.requests *= 1.18
    game_data.energy_consumption_rate *= 1.10
    game_data.power_reliability -= 5


def card11_effect(game_data: GameData) -> None:
    game_data.money *= 1.10
    game_data.requests *= 1.10
    game_data.energy_consumption_rate *= 1.08


def card12_effect(game_data: GameData) -> None:
    game_data.requests *= 1.12
    game_data.energy_consumption_rate *= 1.10
    game_data.power_reliability -= 6


def card13_effect(game_data: GameData) -> None:
    game_data.energy_generation_rate *= 1.08
    game_data.energy_consumption_rate *= 1.10
    game_data.requests *= 1.06


def card14_effect(game_data: GameData) -> None:
    game_data.money *= 0.97
    game_data.population_satisfaction += 5
    game_data.requests *= 1.05


def card15_effect(game_data: GameData) -> None:
    game_data.power_reliability += 10
    game_data.energy_generation_rate *= 0.95
    game_data.money *= 0.97


def card16_effect(game_data: GameData) -> None:
    game_data.energy_consumption_rate *= 1.18
    game_data.water_consumption_rate *= 1.15
    game_data.emissions *= 1.20
    game_data.money *= 2


def card17_effect(game_data: GameData) -> None:
    game_data.energy_generation_rate *= 1.12
    game_data.power_reliability += 5
    game_data.emissions *= 0.92


def card18_effect(game_data: GameData) -> None:
    game_data.emissions *= 0.85
    game_data.population_satisfaction += 25
    game_data.energy_generation_rate *= 0.96


def card19_effect(game_data: GameData) -> None:
    game_data.energy_generation_rate *= 1.10
    game_data.emissions *= 0.90
    game_data.money *= 0.97


def card20_effect(game_data: GameData) -> None:
    game_data.energy_generation_rate *= 1.12
    game_data.emissions *= 0.88
    game_data.money *= 0.96


def card21_effect(game_data: GameData) -> None:
    game_data.electricity_bills *= 1.08
    game_data.money *= 0.94
    game_data.population_satisfaction -= 5


def card22_effect(game_data: GameData) -> None:
    game_data.money *= 1.10
    game_data.requests *= 1.08
    game_data.energy_consumption_rate *= 1.06


def card23_effect(game_data: GameData) -> None:
    game_data.population_satisfaction += 8
    game_data.money *= 1.08
    game_data.requests *= 1.05


def card24_effect(game_data: GameData) -> None:
    game_data.money *= 1.12
    game_data.population_satisfaction += 5
    game_data.requests *= 1.05


def card25_effect(game_data: GameData) -> None:
    game_data.money *= 1.08
    game_data.population_satisfaction += 6
    game_data.requests *= 1.08


def card26_effect(game_data: GameData) -> None:
    game_data.money *= 1.10
    game_data.population_satisfaction += 7
    game_data.requests *= 1.10

    game_data.energy_consumption_rate *= 1.05


def card27_effect(game_data: GameData) -> None:
    # tuna mayo
    game_data.electricity_bills *= 1.12
    game_data.money *= 0.90
    game_data.population_satisfaction -= 6


def card28_effect(game_data: GameData) -> None:
    game_data.electricity_bills *= 1.08
    game_data.money *= 0.94
    game_data.energy_consumption_rate *= 1.05


def card29_effect(game_data: GameData) -> None:
    game_data.electricity_bills *= 1.10
    game_data.money *= 0.93
    game_data.population_satisfaction -= 5


def card30_effect(game_data: GameData) -> None:
    game_data.electricity_bills *= 1.15
    game_data.money *= 0.88
    game_data.population_satisfaction -= 8


def card31_effect(game_data: GameData) -> None:
    game_data.money *= 0.92
    game_data.requests *= 1.12
    game_data.energy_consumption_rate *= 1.08


def card32_effect(game_data: GameData) -> None:
    game_data.energy_consumption_rate *= 1.12
    game_data.emissions *= 1.10
    game_data.energy_generation_rate *= 1.08

    game_data.power_reliability -= 5


def card33_effect(game_data: GameData) -> None:
    game_data.energy_consumption_rate *= 1.10
    game_data.requests *= 1.08
    game_data.power_reliability -= 4


def card34_effect(game_data: GameData) -> None:
    game_data.population_satisfaction += 10
    game_data.money *= 0.95
    game_data.requests *= 1.05


def card35_effect(game_data: GameData) -> None:
    game_data.population_satisfaction += 8
    game_data.requests *= 1.05
    game_data.money *= 0.97


def card36_effect(game_data: GameData) -> None:
    game_data.population_satisfaction += 10_000_000
    game_data.requests *= 1.06
    game_data.money *= 0.96


def card37_effect(game_data: GameData) -> None:
    game_data.population_satisfaction += 5
    game_data.requests *= 0.95
    game_data.money *= 0.98


def card38_effect(game_data: GameData) -> None:
    game_data.population_satisfaction -= 10
    game_data.energy_consumption_rate *= 1.08
    game_data.requests *= 1.05


def card39_effect(game_data: GameData) -> None:
    game_data.water_consumption_rate *= 1.15
    game_data.water *= 0.90
    game_data.population_satisfaction -= 8


def card40_effect(game_data: GameData) -> None:
    game_data.population_satisfaction += 8
    game_data.money *= 0.96
    game_data.requests *= 1.05


def card41_effect(game_data: GameData) -> None:
    game_data.population_satisfaction -= 5
    game_data.money *= 0.97
    game_data.requests *= 1.05


def card42_effect(game_data: GameData) -> None:
    game_data.energy_generation_rate *= 1.10
    game_data.emissions *= 0.85
    game_data.money *= 0.94

    game_data.energy_consumption_rate *= 1.05


def card43_effect(game_data: GameData) -> None:
    game_data.population_satisfaction += 8
    game_data.requests *= 1.05
    game_data.money *= 0.97


def card44_effect(game_data: GameData) -> None:
    game_data.money *= 0.92
    game_data.power_reliability += 8
    game_data.population_satisfaction += 4


def card45_effect(game_data: GameData) -> None:
    game_data.money *= 0.95
    game_data.population_satisfaction += 8
    game_data.requests *= 0.95


# ingus bingus dongus

card1 = Card(name="The Data Centre Boom", description="+12% energy_generation_rate, +8% energy_consumption_rate, -4 power_reliabilityy (Based on CSO electricity consumption)",
             rarity=CardRarity.COMMON, effect=card1_effect)

card2 = Card(name="Demand Surge", description="+15% energy_generation_rate, -5% money, -14 power_reliability (Based on SEAI demand forecast)",
             rarity=CardRarity.UNCOMMON, effect=card2_effect)

card3 = Card(name="Grid Connection Queue", description="+10% energy_generation_rate, -10% energy_consumption_rate, -8 power_reliability (Based on EirGrid demand assessment)",
             rarity=CardRarity.RARE, effect=card3_effect)

card4 = Card(name="Capacity Expansion", description="+10% energy_generation_rate, +8% energy_consumption_rate, +5% requests (Based on BitPower cumulative data)",

             rarity=CardRarity.COMMON, effect=card4_effect)

card5 = Card(name="Construction Wave", description="+8% money, +6% energy_consumption_rate, +5% requests (Based on BitPower annual additions)",

             rarity=CardRarity.UNCOMMON, effect=card5_effect)

card6 = Card(name="Pipeline Overflow", description="+15% energy_generation_rate, +12% energy_consumption_rate, -6 power_reliability (Based on KPMG data centre pipeline)",

             rarity=CardRarity.RARE, effect=card6_effect)

card7 = Card(name="Steady-State Growth", description="+8% energy_consumption_rate, +5% money, -4 power_reliability (Based on KPMG data centre utilisation)",

             rarity=CardRarity.UNCOMMON, effect=card7_effect)

card8 = Card(name="Efficiency Benchmark", description="-8% energy_consumption_rate, -3% money, -4% energy_generation_rate (Based on EU PUE data)",

             rarity=CardRarity.RARE, effect=card8_effect)

card9 = Card(name="Cooling Efficiency", description="-10% water_consumption_rate, -3% money, +4 population_satisfaction (Based on EU WUE data)",

             rarity=CardRarity.UNCOMMON, effect=card9_effect)

card10 = Card(name="Dublin Capacity Boom", description="+8% requests, +10% energy_consumption_rate, -5 power_reliability (Based on KPMG data centre capacity by city)",

              rarity=CardRarity.RARE, effect=card10_effect)

card11 = Card(name="International Expansion", description="+10% money, +10% requests, +8% energy_consumption_rate (Based on KPMG international case studies)",

              rarity=CardRarity.UNCOMMON, effect=card11_effect)

card12 = Card(name="FLAPD Competition", description="+12% requests, +10% energy_consumption_rate, -6 power_reliability (Based on KPMG FLAPD markets)",

              rarity=CardRarity.RARE, effect=card12_effect)

card13 = Card(name="Large Facility", description="+8% energy_generation_rate, +10% energy_consumption_rate, +6% requests (Based on EU data centre size data)",

              rarity=CardRarity.UNCOMMON, effect=card13_effect)

card14 = Card(name="Better Reporting", description="-3% money, +5 population_satisfaction, -5% requests (Based on EU data reporting quality)",

              rarity=CardRarity.COMMON, effect=card14_effect)

card15 = Card(name="Reliable Infrastructure", description="+10 power_reliability, -5% energy_generation_rate, -3% money (Based on EU infrastructure reliability data)",

              rarity=CardRarity.RARE, effect=card15_effect)

card16 = Card(name="Hyperscale Facility", description="+18% energy_consumption_rate, +15% water_consumption_rate, +20% emissions, +15% money (Based on KPMG data centre type data)",

              rarity=CardRarity.LEGENDARY, effect=card16_effect)

card17 = Card(name="Renewable Grid", description="+12% energy_generation_rate, +5 power_reliability, -8% emissions (Based on EirGrid renewable energy data)",

              rarity=CardRarity.RARE, effect=card17_effect)

card18 = Card(name="Cleaner Electricity", description="-15% emissions, +5 population_satisfaction, -4% energy_generation_rate (Based on EirGrid CO2 intensity data)",

              rarity=CardRarity.RARE, effect=card18_effect)

card19 = Card(name="Renewable Energy Share", description="+10% energy_generation_rate, -10% emissions, -3% money (Based on EU renewable energy fraction data)",

              rarity=CardRarity.RARE, effect=card19_effect)

card20 = Card(name="Renewable Power Contract", description="+12% energy_generation_rate, -12% emissions, -4% money (Based on KPMG renewable energy assumptions)",

              rarity=CardRarity.RARE, effect=card20_effect)

card21 = Card(name="Household Electricity Shock", description="+8% electricity_bills, -6% money, -5 population_satisfaction (Based on Fearon household electricity cost data)",

              rarity=CardRarity.UNCOMMON, effect=card21_effect)

card22 = Card(name="Steady Economic Growth", description="+10% money, +8% requests, +6% energy_consumption_rate (Based on KPMG economic scenario data)",

              rarity=CardRarity.UNCOMMON, effect=card22_effect)

card23 = Card(name="Jobs Boom", description="+8 population_satisfaction, +8% money, +5% requests (Based on KPMG employment data)",

              rarity=CardRarity.RARE, effect=card23_effect)

card24 = Card(name="Economic Engine", description="+12% money, +5 population_satisfaction, +5% requests (Based on KPMG gross value added and employment data)",

              rarity=CardRarity.RARE, effect=card24_effect)

card25 = Card(name="Economic Spillover", description="+8% money, +6 population_satisfaction, +8% requests (Based on KPMG direct, indirect and induced economic impacts)",

              rarity=CardRarity.RARE, effect=card25_effect)

card26 = Card(name="Digital Economy Growth", description="+10% money, +7 population_satisfaction, +10% requests, +5% energy_consumption_rate (Based on KPMG enabled economic activity data)",

              rarity=CardRarity.LEGENDARY, effect=card26_effect)

card27 = Card(name="Wholesale Price Effect", description="+12% electricity_bills, -10% money, -6 population_satisfaction (Based on Fearon wholesale price effect)",

              rarity=CardRarity.RARE, effect=card27_effect)

card28 = Card(name="High Demand Prices", description="+8% electricity_bills, -6% money, +5% energy_consumption_rate (Based on Fearon demand scenarios)",

              rarity=CardRarity.UNCOMMON, effect=card28_effect)

card29 = Card(name="Rising Energy Costs", description="+10% electricity_bills, -7% money, -5 population_satisfaction (Based on Fearon household cost scenarios)",

              rarity=CardRarity.RARE, effect=card29_effect)

card30 = Card(name="Price Divergence", description="+15% electricity_bills, -12% money, -8 population_satisfaction (Based on Fearon comparative scenarios)",

              rarity=CardRarity.LEGENDARY, effect=card30_effect)

card31 = Card(name="Investment Rush", description="-8% money, +12% requests, +8% energy_consumption_rate (Based on BitPower construction investment data)",

              rarity=CardRarity.RARE, effect=card31_effect)

card32 = Card(name="Carbon-Heavy Expansion", description="+12% energy_consumption_rate, +10% emissions, +8% energy_generation_rate, -5 power_reliability (Based on BitPower operational estimates)",

              rarity=CardRarity.UNCOMMON, effect=card32_effect)

card33 = Card(name="Regional Concentration", description="+10% energy_consumption_rate, +8% requests, -4 power_reliability (Based on BitPower sub-regional operational data)",

              rarity=CardRarity.RARE, effect=card33_effect)

card34 = Card(name="Community Investment", description="+10 population_satisfaction, -5% money, +5% requests (Based on CyrusOne community impact survey)",

              rarity=CardRarity.COMMON, effect=card34_effect)

card35 = Card(name="Positive Public Perception", description="+8 population_satisfaction, +5% requests, -3% money (Based on CyrusOne public perception survey)",

              rarity=CardRarity.COMMON, effect=card35_effect)

card36 = Card(name="Local Acceptance", description="+10 population_satisfaction, +6% requests, -4% money (Based on CyrusOne local acceptance survey)",

              rarity=CardRarity.UNCOMMON, effect=card36_effect)

card37 = Card(name="Public Awareness", description="+5 population_satisfaction, -5% requests, -2% money (Based on CyrusOne data centre awareness survey)",

              rarity=CardRarity.COMMON, effect=card37_effect)

card38 = Card(name="Community Concerns", description="-10 population_satisfaction, +8% energy_consumption_rate, +5% requests (Based on CyrusOne negative community impact survey)",

              rarity=CardRarity.UNCOMMON, effect=card38_effect)

card39 = Card(name="Water Pressure", description="+15% water_consumption_rate, -10% water, -8 population_satisfaction (Based on Beyond Fossil Fuels water demand survey)",

              rarity=CardRarity.RARE, effect=card39_effect)

card40 = Card(name="Local Benefits Package", description="+8 population_satisfaction, -4% money, +5% requests (Based on CyrusOne community benefit survey)",

              rarity=CardRarity.UNCOMMON, effect=card40_effect)

card41 = Card(name="Amenity Expectations", description="-5 population_satisfaction, -3% money, +5% requests (Based on CyrusOne community amenity survey)",

              rarity=CardRarity.COMMON, effect=card41_effect)

card42 = Card(name="Renewables Only", description="+10% energy_generation_rate, -15% emissions, -6% money, +5% energy_consumption_rate (Based on Beyond Fossil Fuels renewable energy survey)",

              rarity=CardRarity.RARE, effect=card42_effect)

card43 = Card(name="National Support", description="+8 population_satisfaction, +5% requests, -3% money (Based on Beyond Fossil Fuels national support survey)",

              rarity=CardRarity.UNCOMMON, effect=card43_effect)

card44 = Card(name="Grid Contribution", description="-8% money, +8 power_reliability, +4 population_satisfaction (Based on Beyond Fossil Fuels energy grid investment survey)",

              rarity=CardRarity.RARE, effect=card44_effect)

card45 = Card(name="Environmental Disclosure", description="-5% money, +8 population_satisfaction, -5% requests (Based on Beyond Fossil Fuels environmental disclosure survey)",

              rarity=CardRarity.UNCOMMON, effect=card45_effect)


# endregion cards

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
