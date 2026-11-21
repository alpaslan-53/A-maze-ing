"""Maze generator module providing generation, loop injection, and solving."""

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
    "X...XXX",
    "X.....X",
    "XXX.XXX",
    "..X.X..",
    "..X.XXX",
)
PATTERN_WIDTH: int = 7
PATTERN_HEIGHT: int = 5
MIN_WIDTH_FOR_PATTERN: int = 9
MIN_HEIGHT_FOR_PATTERN: int = 7
MIN_LOOPS: int = 2


class MazeGenerator:
    """Core generator that builds and solves grid-based mazes."""

    def __init__(
        self,
        width: int,
        height: int,
        entry: Cell = (0, 0),
        exit: Cell | None = None,
        perfect: bool = False,
        seed: int | None = None,
    ) -> None:
        """Configure maze parameters and initialize state."""
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
        self._validate_basic()

    def _validate_basic(self) -> None:
        """Verify dimensional parameters and cell bounds."""
        if self.width < 2 or self.height < 2:
            raise ValueError("width and height must be at least 2")
        if not self._in_bounds(self.entry[0], self.entry[1]):
            raise ValueError(f"entry {self.entry} is outside the maze")
        if not self._in_bounds(self.exit[0], self.exit[1]):
            raise ValueError(f"exit {self.exit} is outside the maze")
        if self.entry == self.exit:
            raise ValueError("entry and exit must be different cells")

    def _place_pattern(self) -> None:
        """Embed the centered '42' logo within the maze if space permits."""
        if (
            self.width < MIN_WIDTH_FOR_PATTERN
            or self.height < MIN_HEIGHT_FOR_PATTERN
        ):
            self.pattern_drawn = False
            print("Notice: Maze size is too small to draw the '42' pattern.")
            return

        origin_x: int = (self.width - PATTERN_WIDTH) // 2
        origin_y: int = (self.height - PATTERN_HEIGHT) // 2
        pattern: set[Cell] = set()

        for row_idx, row in enumerate(PATTERN_42):
            for col_idx, symbol in enumerate(row):
                if symbol == "X":
                    pattern.add((origin_x + col_idx, origin_y + row_idx))

        if self.entry in pattern or self.exit in pattern:
            raise ValueError("Entry or exit cannot be inside the 42 pattern.")

        self.pattern_cells = pattern
        self.pattern_drawn = True

    def _in_bounds(self, x: int, y: int) -> bool:
        """Determine whether point (x, y) lies inside the maze rectangle."""
        return 0 <= x < self.width and 0 <= y < self.height

    def _open_wall(self, x: int, y: int, direction: Direction) -> None:
        """Clear boundary walls between (x, y) and its adjacent neighbor."""
        target_x: int = x + direction.dx
        target_y: int = y + direction.dy
        if self._in_bounds(target_x, target_y):
            self.grid[y][x] &= ~direction.bit
            self.grid[target_y][target_x] &= ~direction.opposite_bit

    def _close_wall(self, x: int, y: int, direction: Direction) -> None:
        """Restore boundary walls between (x, y) and its adjacent neighbor."""
        target_x: int = x + direction.dx
        target_y: int = y + direction.dy
        if self._in_bounds(target_x, target_y):
            self.grid[y][x] |= direction.bit
            self.grid[target_y][target_x] |= direction.opposite_bit

    def _open_count(self, x: int, y: int) -> int:
        """Calculate the total number of open corridors for a cell."""
        return 4 - self.grid[y][x].bit_count()

    def _is_dead_end(self, x: int, y: int) -> bool:
        """Identify if a cell is an isolated branch with only one exit."""
        if (x, y) in self.pattern_cells:
            return False
        return self._open_count(x, y) == 1

    def _block_is_open(self, bx: int, by: int) -> bool:
        """Check whether a 3x3 square is completely devoid of inner walls."""
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
        """Test if removing a wall introduces an unauthorized open space."""
        target_x: int = x + direction.dx
        target_y: int = y + direction.dy
        self._open_wall(x, y, direction)
        has_open_square: bool = False
        for by in range(max(y, target_y) - 2, min(y, target_y) + 1):
            for bx in range(max(x, target_x) - 2, min(x, target_x) + 1):
                if self._block_is_open(bx, by):
                    has_open_square = True
        self._close_wall(x, y, direction)
        return has_open_square

    def _wall_candidates(self, x: int, y: int) -> list[Direction]:
        """Collect all closed walls that can be knocked down safely."""
        safe_walls: list[Direction] = []
        for d in DIRECTIONS:
            target_x: int = x + d.dx
            target_y: int = y + d.dy
            if (
                not self._in_bounds(target_x, target_y)
                or (target_x, target_y) in self.pattern_cells
            ):
                continue
            if not (self.grid[y][x] & d.bit):
                continue
            if self._makes_open_area(x, y, d):
                continue
            safe_walls.append(d)
        return safe_walls

    def count_loops(self) -> int:
        """Count cyclomatic cycles using graph Euler characteristics."""
        corridors: int = 0
        active_cells: int = 0
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern_cells:
                    continue
                active_cells += 1
                if (
                    x + 1 < self.width
                    and (x + 1, y) not in self.pattern_cells
                    and not (self.grid[y][x] & EAST)
                ):
                    corridors += 1
                if (
                    y + 1 < self.height
                    and (x, y + 1) not in self.pattern_cells
                    and not (self.grid[y][x] & SOUTH)
                ):
                    corridors += 1
        if active_cells == 0:
            return 0
        return max(0, corridors - active_cells + 1)

    def _remove_dead_ends(self) -> None:
        """Eliminate dead ends by opening walls towards adjacent paths."""
        dead_cells: list[Cell] = []
        for y in range(self.height):
            for x in range(self.width):
                if self._is_dead_end(x, y):
                    dead_cells.append((x, y))

        self._rng.shuffle(dead_cells)
        for x, y in dead_cells:
            if not self._is_dead_end(x, y):
                continue
            safe_walls = self._wall_candidates(x, y)
            if not safe_walls:
                continue
            paired_dead_ends = [
                d for d in safe_walls
                if self._is_dead_end(x + d.dx, y + d.dy)
            ]
            chosen_dir = self._rng.choice(
                paired_dead_ends if paired_dead_ends else safe_walls
            )
            self._open_wall(x, y, chosen_dir)

    def _add_minimum_loops(self) -> None:
        """Inject cycles until MIN_LOOPS threshold is guaranteed."""
        available_cells: list[Cell] = []
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in self.pattern_cells:
                    available_cells.append((x, y))

        self._rng.shuffle(available_cells)
        for x, y in available_cells:
            if self.count_loops() >= MIN_LOOPS:
                return
            safe_walls = self._wall_candidates(x, y)
            if safe_walls:
                self._open_wall(x, y, self._rng.choice(safe_walls))

    def _braid(self) -> None:
        """Transform perfect tree maze into looped topology for Pac-Man."""
        self._remove_dead_ends()
        self._add_minimum_loops()

    def _carve_dfs(self, start_x: int, start_y: int) -> None:
        """Excavate maze paths using randomized depth-first search."""
        visited: set[Cell] = {(start_x, start_y)}
        visited.update(self.pattern_cells)
        stack: list[Cell] = [(start_x, start_y)]

        while stack:
            curr_x, curr_y = stack[-1]
            unvisited: list[tuple[Direction, int, int]] = []
            for d in DIRECTIONS:
                next_x: int = curr_x + d.dx
                next_y: int = curr_y + d.dy
                if (
                    self._in_bounds(next_x, next_y)
                    and (next_x, next_y) not in visited
                ):
                    unvisited.append((d, next_x, next_y))

            if unvisited:
                direction, next_x, next_y = self._rng.choice(unvisited)
                self._open_wall(curr_x, curr_y, direction)
                visited.add((next_x, next_y))
                stack.append((next_x, next_y))
            else:
                stack.pop()

    def _solve_bfs(self) -> None:
        """Compute the shortest path across the maze using BFS."""
        if self.entry == self.exit:
            self.solution = ""
            self.solution_cells = [self.entry]
            return

        frontier: deque[Cell] = deque([self.entry])
        visited: set[Cell] = {self.entry}
        came_from: dict[Cell, tuple[Cell, str]] = {}

        while frontier:
            pos_x, pos_y = frontier.popleft()
            if (pos_x, pos_y) == self.exit:
                break

            for d in DIRECTIONS:
                if not (self.grid[pos_y][pos_x] & d.bit):
                    next_x: int = pos_x + d.dx
                    next_y: int = pos_y + d.dy
                    if (
                        self._in_bounds(next_x, next_y)
                        and (next_x, next_y) not in visited
                    ):
                        visited.add((next_x, next_y))
                        came_from[(next_x, next_y)] = ((pos_x, pos_y), d.name)
                        frontier.append((next_x, next_y))

        step_cell: Cell = self.exit
        path_cells: list[Cell] = [step_cell]
        path_chars: list[str] = []

        while step_cell != self.entry:
            if step_cell not in came_from:
                return
            prev_cell, char = came_from[step_cell]
            path_chars.append(char)
            path_cells.append(prev_cell)
            step_cell = prev_cell

        path_chars.reverse()
        path_cells.reverse()
        self.solution = "".join(path_chars)
        self.solution_cells = path_cells

    def generate(self) -> "MazeGenerator":
        """Build the maze layout and calculate its solution."""
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
        if not self.perfect:
            self._braid()
        self._solve_bfs()
        return self
