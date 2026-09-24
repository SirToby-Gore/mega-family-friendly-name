"""THIS CODE IS FULLY AI AND NEEDS REVIEWING. DO NOT TRUST IT WITHOUT CHECKING."""

from dataclasses import replace

from models.game import GameData

INCOME_PER_TICK = 1  # credits per tick; placeholder until balance moves to data/*.json


def step(state: GameData, commands: list[dict]) -> tuple[GameData, list[dict]]:
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

    return state, state.update()
