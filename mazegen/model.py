"""Data models and constants representing maze structures and geometry."""

from typing import NamedTuple

NORTH: int = 1
EAST: int = 2
SOUTH: int = 4
WEST: int = 8
ALL_WALLS: int = 15
NO_WALLS: int = 0

Cell = tuple[int, int]


class Direction(NamedTuple):
    """Encapsulates a movement vector and corresponding wall bitmasks."""

    name: str
    dx: int
    dy: int
    bit: int
    opposite_bit: int


DIRECTIONS: tuple[Direction, ...] = (
    Direction("N", 0, -1, NORTH, SOUTH),
    Direction("E", 1, 0, EAST, WEST),
    Direction("S", 0, 1, SOUTH, NORTH),
    Direction("W", -1, 0, WEST, EAST),
)
