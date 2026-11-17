"""Maze generator module implementing the MazeGenerator class."""

from collections import deque
import random

from mazegen.model import (
    ALL_WALLS,
    Cell,
    DIRECTIONS,
    Direction,
    EAST,
    SOUTH,
)

PATTERN_42: tuple[str, ...] = (
    "X.X.XXX",
    "X.X...X",
    "XXX.XXX",
    "..X.X..",
    "..X.XXX",
)
PATTERN_WIDTH: int = 7
PATTERN_HEIGHT: int = 5
MIN_WIDTH_FOR_PATTERN: int = 9
MIN_HEIGHT_FOR_PATTERN: int = 7


class MazeGenerator:
    """Generates and solves 2D rectangular mazes."""

    def __init__(
        self,
        width: int,
        height: int,
        entry: Cell = (0, 0),
        exit: Cell | None = None,
        perfect: bool = False,
        seed: int | None = None,
    ) -> None:
        """Initialize the maze generator with dimensions and options."""
        self.width: int = width
        self.height: int = height
        self.entry: Cell = entry
        self.perfect: bool = perfect

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

    def _place_pattern(self) -> None:
        """Place the '42' pattern in the center if dimensions allow."""
        if (
            self.width < MIN_WIDTH_FOR_PATTERN
            or self.height < MIN_HEIGHT_FOR_PATTERN
        ):
            self.pattern_drawn = False
            print("Notice: Maze size is too small to draw the '42' pattern.")
            return

        start_x: int = (self.width - PATTERN_WIDTH) // 2
        start_y: int = (self.height - PATTERN_HEIGHT) // 2
        cells: set[Cell] = set()

        for r, row in enumerate(PATTERN_42):
            for c, char in enumerate(row):
                if char == "X":
                    cells.add((start_x + c, start_y + r))

        if self.entry in cells or self.exit in cells:
            raise ValueError("Entry or exit cannot be inside the 42 pattern.")

        self.pattern_cells = cells
        self.pattern_drawn = True

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

    def _close_wall(self, x: int, y: int, direction: Direction) -> None:
        """Close the wall between cell (x, y) and its neighbor in direction."""
        nx: int = x + direction.dx
        ny: int = y + direction.dy
        if self._in_bounds(nx, ny):
            self.grid[y][x] |= direction.bit
            self.grid[ny][nx] |= direction.opposite_bit

    def _open_count(self, x: int, y: int) -> int:
        """Return the number of open passages of a cell."""
        closed_walls: int = bin(self.grid[y][x]).count("1")
        return 4 - closed_walls

    def _is_dead_end(self, x: int, y: int) -> bool:
        """Return True if the cell has exactly one open passage."""
        if (x, y) in self.pattern_cells:
            return False
        return self._open_count(x, y) == 1

    def _block_is_open(self, bx: int, by: int) -> bool:
        """Return True if the 3x3 block at (bx, by) has no inner walls."""
        if bx < 0 or by < 0 or bx + 3 > self.width or by + 3 > self.height:
            return False
        for y in range(by, by + 3):
            for x in range(bx, bx + 3):
                if x < bx + 2 and (self.grid[y][x] & EAST):
                    return False
                if y < by + 2 and (self.grid[y][x] & SOUTH):
                    return False
        return True

    def _makes_open_area(self, x: int, y: int, direction: Direction) -> bool:
        """Check if opening a wall would create an illegal 3x3 open area."""
        nx: int = x + direction.dx
        ny: int = y + direction.dy
        self._open_wall(x, y, direction)
        found: bool = False
        for by in range(max(y, ny) - 2, min(y, ny) + 1):
            for bx in range(max(x, nx) - 2, min(x, nx) + 1):
                if self._block_is_open(bx, by):
                    found = True
        self._close_wall(x, y, direction)
        return found

    def _wall_candidates(self, x: int, y: int) -> list[Direction]:
        """Return closed walls of (x, y) that can safely be opened."""
        candidates: list[Direction] = []
        for d in DIRECTIONS:
            nx: int = x + d.dx
            ny: int = y + d.dy
            if not self._in_bounds(nx, ny):
                continue
            if (nx, ny) in self.pattern_cells:
                continue
            if not (self.grid[y][x] & d.bit):
                continue
            if self._makes_open_area(x, y, d):
                continue
            candidates.append(d)
        return candidates

    def _carve_dfs(self, start_x: int, start_y: int) -> None:
        """Carve maze passages using randomized Depth-First Search."""
        visited: set[Cell] = {(start_x, start_y)}
        visited.update(self.pattern_cells)
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

    def _solve_bfs(self) -> None:
        """Find the shortest path from entry to exit using BFS."""
        if self.entry == self.exit:
            self.solution = ""
            self.solution_cells = [self.entry]
            return

        queue: deque[Cell] = deque([self.entry])
        visited: set[Cell] = {self.entry}
        parent: dict[Cell, tuple[Cell, str]] = {}

        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) == self.exit:
                break

            for d in DIRECTIONS:
                # Duvar açık mı? (bit 0 ise duvar yok demektir)
                if not (self.grid[cy][cx] & d.bit):
                    nx: int = cx + d.dx
                    ny: int = cy + d.dy
                    if self._in_bounds(nx, ny) and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        parent[(nx, ny)] = ((cx, cy), d.name)
                        queue.append((nx, ny))

        # Çıkıştan girişe geri izleme (backtracking)
        curr: Cell = self.exit
        path_cells: list[Cell] = [curr]
        path_chars: list[str] = []

        while curr != self.entry:
            if curr not in parent:
                return
            prev_cell, char = parent[curr]
            path_chars.append(char)
            path_cells.append(prev_cell)
            curr = prev_cell

        path_chars.reverse()
        path_cells.reverse()
        self.solution = "".join(path_chars)
        self.solution_cells = path_cells

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

        self._place_pattern()
        self._carve_dfs(self.entry[0], self.entry[1])
        self._solve_bfs()
        return self
