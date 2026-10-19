"""Maze generator module implementing the MazeGenerator class."""

import random

from mazegen.model import ALL_WALLS, Cell, DIRECTIONS, Direction


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
        self._rng: random.Random = random.Random(self.seed)

    def _in_bounds(self, x: int, y: int) -> bool:
        """Check if coordinates (x, y) are within the maze bounds."""
        return 0 <= x < self.width and 0 <= y < self.height

    def _open_wall(self, x: int, y: int, direction: Direction) -> None:
        """Open the wall between cell (x, y) and its neighbor in direction."""
        nx: int = x + direction.dx
        ny: int = y + direction.dy
        if self._in_bounds(nx, ny):
            self.grid[y][x] &= ~direction.bit
            self.grid[ny][nx] &= ~direction.opposite_bit

    def _carve_dfs(self, start_x: int, start_y: int) -> None:
        """Carve maze passages using randomized Depth-First Search."""
        visited: set[Cell] = {(start_x, start_y)}
        stack: list[Cell] = [(start_x, start_y)]

        while stack:
            cx, cy = stack[-1]
            unvisited: list[tuple[Direction, int, int]] = []
            for d in DIRECTIONS:
                nx: int = cx + d.dx
                ny: int = cy + d.dy
                if self._in_bounds(nx, ny) and (nx, ny) not in visited:
                    unvisited.append((d, nx, ny))

            if unvisited:
                direction, nx, ny = self._rng.choice(unvisited)
                self._open_wall(cx, cy, direction)
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()

    def generate(self) -> "MazeGenerator":
        """Generate a random maze grid using seeded DFS algorithm."""
        self._rng.seed(self.seed)
        grid: list[list[int]] = []
        for _ in range(self.height):
            row: list[int] = []
            for _ in range(self.width):
                row.append(ALL_WALLS)
            grid.append(row)
        self.grid = grid

        self._carve_dfs(self.entry[0], self.entry[1])
        return self
