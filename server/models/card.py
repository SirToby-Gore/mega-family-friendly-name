from typing import Callable
from enum import Enum
import random


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
