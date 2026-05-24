"""Zelda mission definition.

Defines the mission plan for The Legend of Zelda (NES). Each Task
maps to a real in-game objective with concrete success conditions
evaluated against ZeldaStateBuilder output.

This is the only place that knows Zelda's quest structure.
The generic MissionPlan/Task machinery in policy/mission.py has
no game-specific knowledge.

Current mission: Complete the opening sequence through Dungeon 1.

Task sequence
-------------
1. get_wooden_sword    — acquire the wooden sword from the cave
2. reach_dungeon_1     — navigate to Level 1 entrance (grid pos)
3. find_boomerang      — acquire the boomerang inside Dungeon 1
4. defeat_aquamentus   — defeat the Level 1 boss

Success conditions are stubs where the required state fields do not
yet exist. They return False (not started) until the corresponding
perception and state modules are implemented. This is intentional —
the mission structure is correct; the sensors catch up to it.
"""

from __future__ import annotations

from policy.mission import MissionPlan, Task


# ---------------------------------------------------------------------------
# Individual task definitions
# ---------------------------------------------------------------------------

def _get_wooden_sword() -> Task:
    """Acquire the wooden sword from the starting cave.

    Success: state reports sword_acquired == True.
    Stub: returns False until item-pickup detection is implemented.
    """
    return Task(
        name="get_wooden_sword",
        success=lambda state: bool(state.get("sword_acquired", False)),
    )


def _reach_dungeon_1() -> Task:
    """Navigate the overworld to the Dungeon 1 entrance.

    Success: grid position matches known dungeon entrance coords AND
             screen_type transitions to "dungeon".
    Entry:   wooden sword must already be acquired.

    Stub: grid_pos and screen_type not yet in state.
    """
    DUNGEON_1_GRID_POS = (7, 7)  # overworld grid coordinates (col, row)

    return Task(
        name="reach_dungeon_1",
        entry=lambda state: bool(state.get("sword_acquired", False)),
        success=lambda state: (
            state.get("screen_type") == "dungeon"
            and state.get("grid_pos") == DUNGEON_1_GRID_POS
        ),
    )


def _find_boomerang() -> Task:
    """Acquire the boomerang from inside Dungeon 1.

    Success: state reports boomerang_acquired == True.
    Entry:   must be inside a dungeon screen.

    Stub: item acquisition not yet tracked.
    """
    return Task(
        name="find_boomerang",
        entry=lambda state: state.get("screen_type") == "dungeon",
        success=lambda state: bool(state.get("boomerang_acquired", False)),
    )


def _defeat_aquamentus() -> Task:
    """Defeat Aquamentus, the Dungeon 1 boss.

    Success: boss_defeated flag set True in state.
    Entry:   boomerang should be in inventory (preferred, not required).

    Stub: boss detection not yet implemented.
    """
    return Task(
        name="defeat_aquamentus",
        entry=lambda state: bool(state.get("boomerang_acquired", False)),
        success=lambda state: bool(state.get("boss_defeated", False)),
    )


# ---------------------------------------------------------------------------
# Mission factory
# ---------------------------------------------------------------------------

def build_zelda_mission() -> MissionPlan:
    """Construct and return the Zelda opening mission plan.

    Returns:
        MissionPlan ready to be handed to ZeldaPolicy.
    """
    return MissionPlan(
        name="zelda_opening",
        tasks=[
            _get_wooden_sword(),
            _reach_dungeon_1(),
            _find_boomerang(),
            _defeat_aquamentus(),
        ],
    )
