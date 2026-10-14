"""Maze generator module implementing the MazeGenerator class."""

import random

from mazegen.model import ALL_WALLS, Cell


class MazeGenerator:
    """Generates and solves 2D rectangular mazes."""

    def __init__(
        self,
        width: int,
        height: int,
        entry: Cell = (0, 0),
        exit: Cell | None = None,
        seed: int | None = None,
    ) -> None:
        """Initialize the maze generator with dimensions and options."""
        self.width: int = width
        self.height: int = height
        self.entry: Cell = entry

        if exit is not None:
            self.exit: Cell = exit
        else:
            self.exit = (width - 1, height - 1)

        if seed is not None:
            self.seed: int = seed
        else:
            self.seed = random.randrange(2**32)

        self.grid: list[list[int]] = []
        self.solution: str = ""
        self.solution_cells: list[Cell] = []
        self.pattern_cells: set[Cell] = set()
        self.pattern_drawn: bool = False

    def generate(self) -> "MazeGenerator":
        """Generate a closed maze grid where all cells have full walls."""
        grid: list[list[int]] = []
        for _ in range(self.height):
            row: list[int] = []
            for _ in range(self.width):
                row.append(ALL_WALLS)
            grid.append(row)
        self.grid = grid
        return self
