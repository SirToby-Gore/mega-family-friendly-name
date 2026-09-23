from dataclasses import dataclass, asdict

STATE_VERSION = 1


@dataclass
class GameState:
    version: int = STATE_VERSION
    tick: int = 0
    money: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        if data.get("version") != STATE_VERSION:
            raise ValueError(f"Unsupported save version: {data.get('version')}")
        return cls(**data)


def new_game() -> GameState:
    return GameState(money=1000)  # starting cash: 1,000.00