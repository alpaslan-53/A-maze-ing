"""Data models and constants for maze generation.

Defines wall bitmasks, cell coordinates, and cardinal directions.
"""

from typing import NamedTuple

NORTH: int = 1
EAST: int = 2
SOUTH: int = 4
WEST: int = 8
ALL_WALLS: int = 15
NO_WALLS: int = 0

Cell = tuple[int, int]


class Direction(NamedTuple):
    """Represents a movement direction and its wall bitmasks.

    Attributes:
        name: Direction letter ('N', 'E', 'S', 'W').
        dx: Change in x-coordinate (columns).
        dy: Change in y-coordinate (rows).
        bit: Wall bitmask for the current cell.
        opposite_bit: Corresponding wall bitmask for the neighbor.
    """

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
