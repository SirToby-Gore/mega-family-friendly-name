import asyncio
import aiofiles
import asyncio
import websockets
import sim
import models
import api
from enum import Enum


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
print(new_card)


"""
calendar
energy consumption per hit
total water
money
requests
population_satisfaction
energy_generation_rate
water_consumption_rate per hit
power_reliability 1 in x chance per tick of power outage
size (influence on population satisfaction)
emissions (influencve on population satisfaction and water)

LOSS CONDITIONS:
negative money - out of buisness
too low water - burn down/YOU die of thirst
too much water - worldwide drought 
too low population satisfaction - pitchforj riot
too low power reliability - global blackout
too many requesst - short circuit
emissions too high - world submerged
"""
