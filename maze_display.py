"""ANSI terminal visualizer for colorful grid-based maze display."""

import sys

from mazegen import MazeGenerator
from mazegen.model import EAST, SOUTH

WALL_COLOURS: tuple[int, ...] = (255, 27, 34, 220, 208)
PATTERN_COLOURS: tuple[int, ...] = (244, 141, 45, 82)
OPEN_COLOUR: int = 16
PATH_COLOUR: int = 51
ENTRY_COLOUR: int = 46
EXIT_COLOUR: int = 196

RESET: str = "\033[0m"
CLEAR_SCREEN: str = "\033[H\033[2J"


def create_empty_tile_grid(width: int, height: int) -> list[list[str]]:
    """Create a tile grid filled completely with wall tiles."""
    total_rows = 2 * height + 1
    total_cols = 2 * width + 1
    tiles: list[list[str]] = []
    for _ in range(total_rows):
        tiles.append(["wall"] * total_cols)
    return tiles


def carve_rooms_and_passages(
    maze: MazeGenerator, tiles: list[list[str]]
) -> None:
    """Open room centers and remove walls where passages exist."""
    for y in range(maze.height):
        for x in range(maze.width):
            tile_x = 2 * x + 1
            tile_y = 2 * y + 1

            if (x, y) in maze.pattern_cells:
                tiles[tile_y][tile_x] = "pattern"
            else:
                tiles[tile_y][tile_x] = "open"

            cell_walls = maze.grid[y][x]
            east_is_open = (cell_walls & EAST) == 0
            south_is_open = (cell_walls & SOUTH) == 0

            if x + 1 < maze.width and east_is_open:
                tiles[tile_y][tile_x + 1] = "open"
            if y + 1 < maze.height and south_is_open:
                tiles[tile_y + 1][tile_x] = "open"


def connect_pattern_blocks(
    maze: MazeGenerator, tiles: list[list[str]]
) -> None:
    """Fill gaps between adjacent '42' pattern cells so it looks solid."""
    pattern_cells = maze.pattern_cells
    for x, y in pattern_cells:
        tile_x = 2 * x + 1
        tile_y = 2 * y + 1

        has_right = (x + 1, y) in pattern_cells
        has_below = (x, y + 1) in pattern_cells
        has_diagonal = (x + 1, y + 1) in pattern_cells

        if has_right:
            tiles[tile_y][tile_x + 1] = "pattern"
        if has_below:
            tiles[tile_y + 1][tile_x] = "pattern"
        if has_right and has_below and has_diagonal:
            tiles[tile_y + 1][tile_x + 1] = "pattern"


def draw_solution_path(
    maze: MazeGenerator, tiles: list[list[str]]
) -> None:
    """Mark every cell along the shortest path and the gaps between them."""
    path = maze.solution_cells
    for index in range(len(path)):
        x, y = path[index]
        tiles[2 * y + 1][2 * x + 1] = "path"

        if index + 1 < len(path):
            next_x, next_y = path[index + 1]
            gap_x = x + next_x + 1
            gap_y = y + next_y + 1
            tiles[gap_y][gap_x] = "path"


def build_tiles(maze: MazeGenerator, show_path: bool) -> list[list[str]]:
    """Build the full 2D tile map for the maze."""
    tiles = create_empty_tile_grid(maze.width, maze.height)
    carve_rooms_and_passages(maze, tiles)
    connect_pattern_blocks(maze, tiles)

    if show_path:
        draw_solution_path(maze, tiles)

    entry_x, entry_y = maze.entry
    exit_x, exit_y = maze.exit
    tiles[2 * entry_y + 1][2 * entry_x + 1] = "entry"
    tiles[2 * exit_y + 1][2 * exit_x + 1] = "exit"

    return tiles


def render(
    maze: MazeGenerator,
    show_path: bool,
    wall_colour: int,
    pattern_colour: int,
) -> str:
    """Convert the tile map into ANSI colored terminal text."""
    color_map: dict[str, int] = {
        "wall": wall_colour,
        "open": OPEN_COLOUR,
        "path": PATH_COLOUR,
        "entry": ENTRY_COLOUR,
        "exit": EXIT_COLOUR,
        "pattern": pattern_colour,
    }

    tiles = build_tiles(maze, show_path)
    rendered_lines: list[str] = []

    for tile_row in tiles:
        colored_row = ""
        for tile_name in tile_row:
            color_code = color_map[tile_name]
            colored_row = colored_row + f"\033[48;5;{color_code}m  "
        rendered_lines.append(colored_row + RESET)

    return "\n".join(rendered_lines)


def show(
    maze: MazeGenerator,
    show_path: bool,
    wall_colour: int,
    pattern_colour: int,
) -> None:
    """Clear the terminal screen and print the maze with status info."""
    if sys.stdout.isatty():
        print(CLEAR_SCREEN, end="")

    maze_picture = render(maze, show_path, wall_colour, pattern_colour)
    print(maze_picture)

    path_length = len(maze.solution)
    print(
        f"Seed: {maze.seed} | Perfect: {maze.perfect} | "
        f"Path length: {path_length}"
    )

    if not maze.pattern_drawn:
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
