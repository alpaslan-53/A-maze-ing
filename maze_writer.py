"""Export generated maze data into standard hexadecimal output format."""

from typing import Protocol


class MazeLike(Protocol):
    """Structural protocol defining required maze properties."""

    grid: list[list[int]]
    entry: tuple[int, int]
    exit: tuple[int, int]
    solution: str


def build_text(maze: MazeLike) -> str:
    """Format grid, endpoints, and solution string as hex output."""
    output_lines = [
        "".join(f"{hex_cell:X}" for hex_cell in row)
        for row in maze.grid
    ]
    output_lines.append("")
    output_lines.append(f"{maze.entry[0]},{maze.entry[1]}")
    output_lines.append(f"{maze.exit[0]},{maze.exit[1]}")
    output_lines.append(maze.solution)
    return "\n".join(output_lines) + "\n"


def write_maze(maze: MazeLike, path: str) -> None:
    """Write formatted hexadecimal maze text directly to destination path."""
    with open(path, "w", encoding="utf-8", newline="\n") as target_file:
        target_file.write(build_text(maze))
