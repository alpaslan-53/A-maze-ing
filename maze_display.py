"""Terminal display of the maze (colored blocks, ANSI codes).

Each cell is drawn with a grid of tiles: the maze (width x height cells)
becomes (2*width+1) x (2*height+1) tiles. A tile is 2 characters wide so
that it looks like a square.
"""

import sys
from mazegen.model import EAST, SOUTH

WALL_COLOURS: tuple[int, ...] = (255, 27, 34, 220, 208)
PATTERN_COLOURS: tuple[int, ...] = (244, 141, 45, 82)
OPEN_COLOUR: int = 16
PATH_COLOUR: int = 51
ENTRY_COLOUR: int = 46
EXIT_COLOUR: int = 196

RESET: str = "\033[0m"
CLEAR_SCREEN: str = "\033[H\033[2J"


def _join_pattern_tiles(maze: object, tiles: list[list[str]]) -> None:
    """Fill gaps between adjacent '42' cells so the pattern looks solid."""
    cells = getattr(maze, "pattern_cells", set())
    for x, y in cells:
        if (x + 1, y) in cells:
            tiles[2 * y + 1][2 * x + 2] = "pattern"
        if (x, y + 1) in cells:
            tiles[2 * y + 2][2 * x + 1] = "pattern"
        if {(x + 1, y), (x, y + 1), (x + 1, y + 1)} <= cells:
            tiles[2 * y + 2][2 * x + 2] = "pattern"


def build_tiles(maze: object, show_path: bool) -> list[list[str]]:
    """Convert the maze into a grid of tile names."""
    width: int = getattr(maze, "width")
    height: int = getattr(maze, "height")
    grid: list[list[int]] = getattr(maze, "grid")
    pattern_cells = getattr(maze, "pattern_cells", set())

    tiles: list[list[str]] = [
        ["wall"] * (2 * width + 1) for _ in range(2 * height + 1)
    ]
    for y in range(height):
        for x in range(width):
            is_pattern = (x, y) in pattern_cells
            tiles[2 * y + 1][2 * x + 1] = "pattern" if is_pattern else "open"
            if x + 1 < width and not (grid[y][x] & EAST):
                tiles[2 * y + 1][2 * x + 2] = "open"
            if y + 1 < height and not (grid[y][x] & SOUTH):
                tiles[2 * y + 2][2 * x + 1] = "open"

    _join_pattern_tiles(maze, tiles)

    if show_path:
        solution_cells = getattr(maze, "solution_cells", [])
        for cx, cy in solution_cells:
            tiles[2 * cy + 1][2 * cx + 1] = "path"
        for (ax, ay), (bx, by) in zip(solution_cells, solution_cells[1:]):
            tiles[ay + by + 1][ax + bx + 1] = "path"

    entry: tuple[int, int] = getattr(maze, "entry", (0, 0))
    exit_c: tuple[int, int] = getattr(maze, "exit", (width - 1, height - 1))
    tiles[2 * entry[1] + 1][2 * entry[0] + 1] = "entry"
    tiles[2 * exit_c[1] + 1][2 * exit_c[0] + 1] = "exit"

    return tiles


def render(
    maze: object,
    show_path: bool,
    wall_colour: int,
    pattern_colour: int,
) -> str:
    """Return the colored text picture of the maze."""
    colours: dict[str, int] = {
        "wall": wall_colour,
        "open": OPEN_COLOUR,
        "path": PATH_COLOUR,
        "entry": ENTRY_COLOUR,
        "exit": EXIT_COLOUR,
        "pattern": pattern_colour,
    }
    lines: list[str] = []
    for row in build_tiles(maze, show_path):
        line = "".join(f"\033[48;5;{colours[name]}m  " for name in row)
        lines.append(line + RESET)
    return "\n".join(lines)


def show(
    maze: object,
    show_path: bool,
    wall_colour: int,
    pattern_colour: int,
) -> None:
    """Clear the screen on a terminal and print the maze with status info."""
    if sys.stdout.isatty():
        print(CLEAR_SCREEN, end="")
    print(render(maze, show_path, wall_colour, pattern_colour))
    seed = getattr(maze, "seed", None)
    perfect = getattr(maze, "perfect", True)
    sol_len = len(getattr(maze, "solution", ""))
    print(f"Seed: {seed} | Perfect: {perfect} | Path length: {sol_len}")
    if not getattr(maze, "pattern_drawn", True):
        print(
            "Warning: Maze is too small for the '42' pattern (min 9x7), "
            "pattern was omitted.",
            file=sys.stderr,
        )


def print_menu() -> None:
    """Print the interactive menu options."""
    print("=== A-Maze-ing ===")
    print("1. Re-generate a new maze")
    print("2. Show / Hide the shortest path")
    print("3. Rotate the wall colours")
    print("4. Rotate the 42 pattern colours")
    print("5. Quit")
