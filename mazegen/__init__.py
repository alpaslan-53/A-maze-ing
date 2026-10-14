"""Maze generation package.

Exports the MazeGenerator class and core data models.
"""

from mazegen.generator import MazeGenerator
from mazegen.model import (
    ALL_WALLS,
    DIRECTIONS,
    EAST,
    NO_WALLS,
    NORTH,
    SOUTH,
    WEST,
    Cell,
    Direction,
)

__all__ = [
    "MazeGenerator",
    "Cell",
    "Direction",
    "DIRECTIONS",
    "NORTH",
    "EAST",
    "SOUTH",
    "WEST",
    "ALL_WALLS",
    "NO_WALLS",
]
