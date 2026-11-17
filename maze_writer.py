"""Write a generated maze to the output file (hexadecimal format)."""

from typing import Protocol


class MazeLike(Protocol):
    """Protocol for maze objects containing grid and solution attributes."""

    grid: list[list[int]]
    entry: tuple[int, int]
    exit: tuple[int, int]
    solution: str


def build_text(maze: MazeLike) -> str:
    """Return the content of the output file in hexadecimal format."""
    lines = ["".join(f"{cell:X}" for cell in row) for row in maze.grid]
    lines.append("")
    lines.append(f"{maze.entry[0]},{maze.entry[1]}")
    lines.append(f"{maze.exit[0]},{maze.exit[1]}")
    lines.append(maze.solution)
    return "\n".join(lines) + "\n"


def write_maze(maze: MazeLike, path: str) -> None:
    """Save the maze text to a file at the given path."""
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(build_text(maze))
