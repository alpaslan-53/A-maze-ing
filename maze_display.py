"""ANSI terminal visualizer for colorful grid-based maze display."""

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
    """Connect adjacent '42' pattern blocks so the glyph renders unbroken."""
    pattern_coords = getattr(maze, "pattern_cells", set())
    for px, py in pattern_coords:
        if (px + 1, py) in pattern_coords:
            tiles[2 * py + 1][2 * px + 2] = "pattern"
        if (px, py + 1) in pattern_coords:
            tiles[2 * py + 2][2 * px + 1] = "pattern"
        if {(px + 1, py), (px, py + 1), (px + 1, py + 1)} <= pattern_coords:
            tiles[2 * py + 2][2 * px + 2] = "pattern"


def build_tiles(maze: object, show_path: bool) -> list[list[str]]:
    """Transform abstract grid cells into a 2D tile canvas."""
    grid_w: int = getattr(maze, "width")
    grid_h: int = getattr(maze, "height")
    cell_matrix: list[list[int]] = getattr(maze, "grid")
    pattern_coords = getattr(maze, "pattern_cells", set())

    canvas_tiles: list[list[str]] = [
        ["wall"] * (2 * grid_w + 1) for _ in range(2 * grid_h + 1)
    ]
    for row in range(grid_h):
        for col in range(grid_w):
            is_logo = (col, row) in pattern_coords
            canvas_tiles[2 * row + 1][2 * col + 1] = (
                "pattern" if is_logo else "open"
            )
            if col + 1 < grid_w and not (cell_matrix[row][col] & EAST):
                canvas_tiles[2 * row + 1][2 * col + 2] = "open"
            if row + 1 < grid_h and not (cell_matrix[row][col] & SOUTH):
                canvas_tiles[2 * row + 2][2 * col + 1] = "open"

    _join_pattern_tiles(maze, canvas_tiles)

    if show_path:
        solution_nodes = getattr(maze, "solution_cells", [])
        for sx, sy in solution_nodes:
            canvas_tiles[2 * sy + 1][2 * sx + 1] = "path"
        for (x1, y1), (x2, y2) in zip(solution_nodes, solution_nodes[1:]):
            canvas_tiles[y1 + y2 + 1][x1 + x2 + 1] = "path"

    start_pos: tuple[int, int] = getattr(maze, "entry", (0, 0))
    finish_pos: tuple[int, int] = getattr(
        maze, "exit", (grid_w - 1, grid_h - 1)
    )
    canvas_tiles[2 * start_pos[1] + 1][2 * start_pos[0] + 1] = "entry"
    canvas_tiles[2 * finish_pos[1] + 1][2 * finish_pos[0] + 1] = "exit"

    return canvas_tiles


def render(
    maze: object,
    show_path: bool,
    wall_colour: int,
    pattern_colour: int,
) -> str:
    """Generate color-coded terminal text representation of the maze."""
    palette: dict[str, int] = {
        "wall": wall_colour,
        "open": OPEN_COLOUR,
        "path": PATH_COLOUR,
        "entry": ENTRY_COLOUR,
        "exit": EXIT_COLOUR,
        "pattern": pattern_colour,
    }
    rendered_rows: list[str] = []
    for tile_row in build_tiles(maze, show_path):
        row_str = "".join(f"\033[48;5;{palette[name]}m  " for name in tile_row)
        rendered_rows.append(row_str + RESET)
    return "\n".join(rendered_rows)


def show(
    maze: object,
    show_path: bool,
    wall_colour: int,
    pattern_colour: int,
) -> None:
    """Render the maze in terminal alongside generation parameters."""
    if sys.stdout.isatty():
        print(CLEAR_SCREEN, end="")
    print(render(maze, show_path, wall_colour, pattern_colour))
    cur_seed = getattr(maze, "seed", None)
    cur_perfect = getattr(maze, "perfect", True)
    path_len = len(getattr(maze, "solution", ""))
    print(
        f"Seed: {cur_seed} | Perfect: {cur_perfect} | Path length: {path_len}"
    )
    if not getattr(maze, "pattern_drawn", True):
        print(
            "Warning: Maze is too small for the '42' pattern (min 9x7), "
            "pattern was omitted.",
            file=sys.stderr,
        )


def print_menu() -> None:
    """Display interactive console actions for user control."""
    print("=== A-Maze-ing ===")
    print("1. Re-generate a new maze")
    print("2. Show / Hide the shortest path")
    print("3. Rotate the wall colours")
    print("4. Rotate the 42 pattern colours")
    print("5. Quit")
