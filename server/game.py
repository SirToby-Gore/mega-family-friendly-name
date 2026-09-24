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
        return f"{self.name}: {self.description} (Rarity: {self.rarity.value})"

    @staticmethod
    def spawn():
        random_number = random.randint(1, 100)
        if random_number <= 60:
            pos = random.randint(0, len(common_cards) - 1)
            return common_cards[pos]
        elif random_number <= 90:
            pos = random.randint(0, len(uncommon_cards) - 1)
            return uncommon_cards[pos]
        elif random_number <= 99:
            pos = random.randint(0, len(rare_cards) - 1)
            return rare_cards[pos]
        else:
            pos = random.randint(0, len(legendary_cards) - 1)
            return legendary_cards[pos]


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
            "reason": self.reason,
            "energy-generation-level": self.energy_upgrade.level,
            "water-collection-level": self.water_upgrade.level,
            "level-cap": self.level_cap
        }

    def step(self, commands: list[dict]) -> list[dict]:
        results = []
        if self.money<0:
            self.defeat==True
            self.reason=""
        if self.water<0:
            self.defeat==True
            self.reason=""
        if self.water>1000:
            self.defeat==True
            self.reason=""
        if self.population_satisfaction<0:
            self.defeat==True
            self.reason=""
        if self.power_reliability<0:
            self.defeat==True
            self.reason=""
        if self.emissions>10000:
            self.defeat==True
            self.reason=""
        if self.requests>self.electricity/2:
            self.defeat==True
            self.reason=""




        if self.defeat==True:
            return

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
    game_data.energy_generation_rate *= 1.08
    game_data.energy_consumption_rate *= 1.06
    game_data.power_reliability -= 2


def card2_effect(game_data: GameData) -> None:
    game_data.money *= 1.04
    game_data.energy_generation_rate *= 1.08
    game_data.power_reliability -= 4


def card3_effect(game_data: GameData) -> None:
    game_data.energy_generation_rate *= 1.06
    game_data.energy_consumption_rate *= 0.96
    game_data.power_reliability -= 3


def card4_effect(game_data: GameData) -> None:
    game_data.energy_generation_rate *= 1.06
    game_data.energy_consumption_rate *= 1.05
    game_data.requests *= 1.04


def card5_effect(game_data: GameData) -> None:
    game_data.money *= 1.05
    game_data.energy_consumption_rate *= 1.04
    game_data.requests *= 1.03


def card6_effect(game_data: GameData) -> None:
    game_data.energy_generation_rate *= 1.08
    game_data.energy_consumption_rate *= 1.07
    game_data.power_reliability -= 4


def card7_effect(game_data: GameData) -> None:
    game_data.energy_consumption_rate *= 1.06
    game_data.money *= 1.04
    game_data.power_reliability -= 2


def card8_effect(game_data: GameData) -> None:
    game_data.energy_consumption_rate *= 0.94
    game_data.money *= 0.98
    game_data.energy_generation_rate *= 0.97


def card9_effect(game_data: GameData) -> None:
    game_data.water_consumption_rate *= 0.94
    game_data.money *= 0.98
    game_data.population_satisfaction += 2


def card10_effect(game_data: GameData) -> None:
    game_data.requests *= 1.06
    game_data.energy_consumption_rate *= 1.05
    game_data.power_reliability -= 2


def card11_effect(game_data: GameData) -> None:
    game_data.money *= 1.06
    game_data.requests *= 1.06
    game_data.energy_consumption_rate *= 1.04


def card12_effect(game_data: GameData) -> None:
    game_data.requests *= 1.08
    game_data.energy_consumption_rate *= 1.06
    game_data.power_reliability -= 3


def card13_effect(game_data: GameData) -> None:
    game_data.energy_generation_rate *= 1.05
    game_data.energy_consumption_rate *= 1.06
    game_data.requests *= 1.04


def card14_effect(game_data: GameData) -> None:
    game_data.money *= 0.98
    game_data.population_satisfaction += 3
    game_data.requests *= 0.97


def card15_effect(game_data: GameData) -> None:
    game_data.power_reliability += 5
    game_data.energy_generation_rate *= 0.96
    game_data.money *= 0.98


def card16_effect(game_data: GameData) -> None:
    game_data.energy_consumption_rate *= 1.10
    game_data.water_consumption_rate *= 1.08
    game_data.emissions += 8
    game_data.money *= 1.08


def card17_effect(game_data: GameData) -> None:
    game_data.energy_generation_rate *= 1.08
    game_data.power_reliability += 4
    game_data.emissions -= 3


def card18_effect(game_data: GameData) -> None:
    game_data.emissions -= 4
    game_data.population_satisfaction += 3
    game_data.energy_generation_rate *= 0.97


def card19_effect(game_data: GameData) -> None:
    game_data.energy_generation_rate *= 1.06
    game_data.emissions -= 3
    game_data.money *= 0.98


def card20_effect(game_data: GameData) -> None:
    game_data.energy_generation_rate *= 1.07
    game_data.emissions -= 4
    game_data.money *= 0.97


def card21_effect(game_data: GameData) -> None:
    game_data.electricity_bills *= 1.06
    game_data.money *= 0.97
    game_data.population_satisfaction -= 3


def card22_effect(game_data: GameData) -> None:
    game_data.money *= 1.06
    game_data.requests *= 1.05
    game_data.energy_consumption_rate *= 1.04


def card23_effect(game_data: GameData) -> None:
    game_data.population_satisfaction += 5
    game_data.money *= 1.05
    game_data.requests *= 1.03


def card24_effect(game_data: GameData) -> None:
    game_data.money *= 1.07
    game_data.population_satisfaction += 3
    game_data.requests *= 1.03


def card25_effect(game_data: GameData) -> None:
    game_data.money *= 1.05
    game_data.population_satisfaction += 4
    game_data.requests *= 1.05


def card26_effect(game_data: GameData) -> None:
    game_data.money *= 1.08
    game_data.population_satisfaction += 5
    game_data.requests *= 1.06
    game_data.energy_consumption_rate *= 1.04


def card27_effect(game_data: GameData) -> None:
    game_data.electricity_bills *= 1.08
    game_data.money *= 0.95
    game_data.population_satisfaction -= 4


def card28_effect(game_data: GameData) -> None:
    game_data.electricity_bills *= 1.05
    game_data.money *= 0.97
    game_data.energy_consumption_rate *= 1.04


def card29_effect(game_data: GameData) -> None:
    game_data.electricity_bills *= 1.07
    game_data.money *= 0.96
    game_data.population_satisfaction -= 3


def card30_effect(game_data: GameData) -> None:
    game_data.electricity_bills *= 1.10
    game_data.money *= 0.9
    game_data.population_satisfaction -= 5


def card31_effect(game_data: GameData) -> None:
    game_data.money *= 0.97
    game_data.requests *= 1.07
    game_data.energy_consumption_rate *= 1.06


def card32_effect(game_data: GameData) -> None:
    game_data.energy_consumption_rate *= 1.07
    game_data.emissions += 5
    game_data.energy_generation_rate *= 1.05
    game_data.power_reliability -= 2


def card33_effect(game_data: GameData) -> None:
    game_data.energy_consumption_rate *= 1.06
    game_data.requests *= 1.05
    game_data.power_reliability -= 2


def card34_effect(game_data: GameData) -> None:
    game_data.population_satisfaction += 5
    game_data.money *= 0.97
    game_data.requests *= 1.03


def card35_effect(game_data: GameData) -> None:
    game_data.population_satisfaction += 4
    game_data.requests *= 1.03
    game_data.money *= 0.98


def card36_effect(game_data: GameData) -> None:
    game_data.population_satisfaction += 5
    game_data.requests *= 1.04
    game_data.money *= 0.97


def card37_effect(game_data: GameData) -> None:
    game_data.population_satisfaction += 3
    game_data.requests *= 0.97
    game_data.money *= 0.99


def card38_effect(game_data: GameData) -> None:
    game_data.population_satisfaction -= 6
    game_data.energy_consumption_rate *= 1.05
    game_data.requests *= 1.03


def card39_effect(game_data: GameData) -> None:
    game_data.water_consumption_rate *= 1.08
    game_data.water -= 5
    game_data.population_satisfaction -= 4


def card40_effect(game_data: GameData) -> None:
    game_data.population_satisfaction += 4
    game_data.money *= 0.98
    game_data.requests *= 1.03


def card41_effect(game_data: GameData) -> None:
    game_data.population_satisfaction -= 3
    game_data.money *= 0.99
    game_data.requests *= 1.03


def card42_effect(game_data: GameData) -> None:
    game_data.energy_generation_rate *= 1.06
    game_data.emissions -= 5
    game_data.money *= 0.97
    game_data.energy_consumption_rate *= 1.03


def card43_effect(game_data: GameData) -> None:
    game_data.population_satisfaction += 4
    game_data.requests *= 1.03
    game_data.money *= 0.98


def card44_effect(game_data: GameData) -> None:
    game_data.money *= 0.96
    game_data.power_reliability += 5
    game_data.population_satisfaction += 2


def card45_effect(game_data: GameData) -> None:
    game_data.money *= 0.97
    game_data.population_satisfaction += 5
    game_data.requests *= 0.97


card1 = Card(name="Consumption Onslaught", description="+6% energy_generation_rate, +5% energy_consumption_rate, +4% requests (Based on CSO DC Electricity Consumption )",
             rarity=CardRarity.COMMON, effect=card1_effect)

card2 = Card(name="Demand Storm", description="+5% money, +4% energy_consumption_rate, +3% requests (Based on SEAI DC Demand Forecast)",
             rarity=CardRarity.UNCOMMON, effect=card2_effect)

card3 = Card(name="Voltage Overload", description="+8% energy_generation_rate, +7% energy_consumption_rate, -4 power_reliability (Based on KEirGrid Adequ Assess DC F4.1)",
             rarity=CardRarity.RARE, effect=card3_effect)

card4 = Card(name="Capacity Expansion", description="+6% energy_generation_rate, +5% energy_consumption_rate, +4% requests (Based on BitPower cumulative data)",
             rarity=CardRarity.COMMON, effect=card4_effect)

card5 = Card(name="Construction Wave", description="+5% money, +4% energy_consumption_rate, +3% requests (Based on BitPower annual additions)",
             rarity=CardRarity.UNCOMMON, effect=card5_effect)

card6 = Card(name="Pipeline Overflow", description="+8% energy_generation_rate, +7% energy_consumption_rate, -4 power_reliability (Based on KPMG data centre pipeline)",
             rarity=CardRarity.RARE, effect=card6_effect)

card7 = Card(name="Steady-State Growth", description="+6% energy_consumption_rate, +4% money, -2 power_reliability (Based on KPMG data centre utilisation)",
             rarity=CardRarity.UNCOMMON, effect=card7_effect)

card8 = Card(name="Efficiency Benchmark", description="-6% energy_consumption_rate, -2% money, -3% energy_generation_rate (Based on EU PUE data)",
             rarity=CardRarity.RARE, effect=card8_effect)

card9 = Card(name="Cooling Efficiency", description="-6% water_consumption_rate, -2% money, +2 population_satisfaction (Based on EU WUE data)",
             rarity=CardRarity.UNCOMMON, effect=card9_effect)

card10 = Card(name="Dublin Capacity Boom", description="+6% requests, +5% energy_consumption_rate, -2 power_reliability (Based on KPMG data centre capacity by city)",
              rarity=CardRarity.RARE, effect=card10_effect)

card11 = Card(name="International Expansion", description="+6% money, +6% requests, +4% energy_consumption_rate (Based on KPMG international case studies)",
              rarity=CardRarity.UNCOMMON, effect=card11_effect)

card12 = Card(name="FLAPD Competition", description="+8% requests, +6% energy_consumption_rate, -3 power_reliability (Based on KPMG FLAPD markets)",

              rarity=CardRarity.RARE, effect=card12_effect)
card13 = Card(name="Large Facility", description="+5% energy_generation_rate, +6% energy_consumption_rate, +4% requests (Based on EU data centre size data)",
              rarity=CardRarity.UNCOMMON, effect=card13_effect)

card14 = Card(name="Better Reporting", description="-2% money, +3 population_satisfaction, -3% requests (Based on EU data reporting quality)",
              rarity=CardRarity.COMMON, effect=card14_effect)

card15 = Card(name="Reliable Infrastructure", description="+5 power_reliability, -4% energy_generation_rate, -2% money (Based on EU infrastructure reliability data)",
              rarity=CardRarity.RARE, effect=card15_effect)

card16 = Card(name="Hyperscale Facility", description="+10% energy_consumption_rate, +8% water_consumption_rate, +8 emissions, +8% money (Based on KPMG data centre type data)",
              rarity=CardRarity.LEGENDARY, effect=card16_effect)

card17 = Card(name="Renewable Grid", description="+8% energy_generation_rate, +4 power_reliability, -3 emissions (Based on EirGrid renewable energy data)",
              rarity=CardRarity.RARE, effect=card17_effect)

card18 = Card(name="Cleaner Electricity", description="-4 emissions, +3 population_satisfaction, -3% energy_generation_rate (Based on EirGrid CO2 intensity data)",
              rarity=CardRarity.RARE, effect=card18_effect)

card19 = Card(name="Renewable Energy Share", description="+6% energy_generation_rate, -3 emissions, -2% money (Based on EU renewable energy fraction data)",
              rarity=CardRarity.RARE, effect=card19_effect)

card20 = Card(name="Renewable Power Contract", description="+7% energy_generation_rate, -4 emissions, -3% money (Based on KPMG renewable energy assumptions)",
              rarity=CardRarity.RARE, effect=card20_effect)

card21 = Card(name="Household Electricity Shock", description="+6% electricity_bills, -3% money, -3 population_satisfaction (Based on Fearon household electricity cost data)",
              rarity=CardRarity.UNCOMMON, effect=card21_effect)

card22 = Card(name="Steady Economic Growth", description="+6% money, +5% requests, +4% energy_consumption_rate (Based on KPMG economic scenario data)",
              rarity=CardRarity.UNCOMMON, effect=card22_effect)

card23 = Card(name="Jobs Boom", description="+5 population_satisfaction, +5% money, +3% requests (Based on KPMG employment data)",
              rarity=CardRarity.RARE, effect=card23_effect)

card24 = Card(name="Economic Engine", description="+7% money, +3 population_satisfaction, +3% requests (Based on KPMG gross value added and employment data)",
              rarity=CardRarity.RARE, effect=card24_effect)

card25 = Card(name="Economic Spillover", description="+5% money, +4 population_satisfaction, +5% requests (Based on KPMG direct, indirect and induced economic impacts)",
              rarity=CardRarity.RARE, effect=card25_effect)

card26 = Card(name="Digital Economy Growth", description="+8% money, +5 population_satisfaction, +6% requests, +4% energy_consumption_rate (Based on KPMG enabled economic activity data)",
              rarity=CardRarity.LEGENDARY, effect=card26_effect)

card27 = Card(name="Wholesale Price Effect", description="+8% electricity_bills, -5% money, -4 population_satisfaction (Based on Fearon wholesale price effect)",
              rarity=CardRarity.RARE, effect=card27_effect)

card28 = Card(name="High Demand Prices", description="+5% electricity_bills, -3% money, +4% energy_consumption_rate (Based on Fearon demand scenarios)",
              rarity=CardRarity.UNCOMMON, effect=card28_effect)

card29 = Card(name="Rising Energy Costs", description="+7% electricity_bills, -4% money, -3 population_satisfaction (Based on Fearon household cost scenarios)",
              rarity=CardRarity.RARE, effect=card29_effect)

card30 = Card(name="Price Divergence", description="+10% electricity_bills, -7% money, -5 population_satisfaction (Based on Fearon comparative scenarios)",
              rarity=CardRarity.LEGENDARY, effect=card30_effect)

card31 = Card(name="Investment Rush", description="-3% money, +7% requests, +6% energy_consumption_rate (Based on BitPower construction investment data)",
              rarity=CardRarity.RARE, effect=card31_effect)

card32 = Card(name="Carbon-Heavy Expansion", description="+7% energy_consumption_rate, +5 emissions, +5% energy_generation_rate, -2 power_reliability (Based on BitPower operational estimates)",
              rarity=CardRarity.UNCOMMON, effect=card32_effect)

card33 = Card(name="Regional Concentration", description="+6% energy_consumption_rate, +5% requests, -2 power_reliability (Based on BitPower sub-regional operational data)",
              rarity=CardRarity.RARE, effect=card33_effect)

card34 = Card(name="Community Investment", description="+5 population_satisfaction, -3% money, +3% requests (Based on CyrusOne community impact survey)",
              rarity=CardRarity.COMMON, effect=card34_effect)

card35 = Card(name="Positive Public Perception", description="+4 population_satisfaction, +3% requests, -2% money (Based on CyrusOne public perception survey)",
              rarity=CardRarity.COMMON, effect=card35_effect)

card36 = Card(name="Local Acceptance", description="+5 population_satisfaction, +4% requests, -3% money (Based on CyrusOne local acceptance survey)",
              rarity=CardRarity.UNCOMMON, effect=card36_effect)

card37 = Card(name="Public Awareness", description="+3 population_satisfaction, -3% requests, -1% money (Based on CyrusOne data centre awareness survey)",
              rarity=CardRarity.COMMON, effect=card37_effect)

card38 = Card(name="Community Concerns", description="-6 population_satisfaction, +5% energy_consumption_rate, +3% requests (Based on CyrusOne negative community impact survey)",
              rarity=CardRarity.UNCOMMON, effect=card38_effect)

card39 = Card(name="Water Pressure", description="+8% water_consumption_rate, -5 water, -4 population_satisfaction (Based on Beyond Fossil Fuels water demad survey)",
              rarity=CardRarity.RARE, effect=card39_effect)

card40 = Card(name="Local Benefits Package", description="+4 population_satisfaction, -2% money, +3% requests (Based on CyrusOne community benefit survey)",
              rarity=CardRarity.UNCOMMON, effect=card40_effect)

card41 = Card(name="Amenity Expectations", description="-3 population_satisfaction, -1% money, +3% requests (Based on CyrusOne community amenity survey)",
              rarity=CardRarity.COMMON, effect=card41_effect)

card42 = Card(name="Renewables Only", description="+6% energy_generation_rate, -5 emissions, -3% money, +3% energy_consumption_rate (Based on Beyond Fossil Fuels renewable energy survey)",
              rarity=CardRarity.RARE, effect=card42_effect)

card43 = Card(name="National Support", description="+4 population_satisfaction, +3% requests, -2% money (Based on Beyond Fossil Fuels national support survey)",
              rarity=CardRarity.UNCOMMON, effect=card43_effect)

card44 = Card(name="Grid Contribution", description="-4% money, +5 power_reliability, +2 population_satisfaction (Based on Beyond Fossil Fuels energy grid investment survey)",
              rarity=CardRarity.RARE, effect=card44_effect)

card45 = Card(name="Environmental Disclosure", description="-3% money, +5 population_satisfaction, -3% requests (Based on Beyond Fossil Fuels environmental disclosure survey)",
              rarity=CardRarity.UNCOMMON, effect=card45_effect)


common_cards = [
    card1,
    card4,
    card14,
    card34,
    card35,
    card37,
    card41
]

uncommon_cards = [
    card2,
    card5,
    card7,
    card9,
    card11,
    card13,
    card21,
    card22,
    card28,
    card32,
    card36,
    card38,
    card40,
    card43,
    card45
]

rare_cards = [
    card3,
    card6,
    card8,
    card10,
    card12,
    card15,
    card17,
    card18,
    card19,
    card20,
    card23,
    card24,
    card25,
    card27,
    card29,
    card31,
    card33,
    card39,
    card42,
    card44
]

legendary_cards = [
    card16,
    card26,
    card30
]

print(Card.spawn())
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

