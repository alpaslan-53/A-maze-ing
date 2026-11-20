"""A-Maze-ing: generate a maze from a config file and display it.

Usage:
    python3 a_maze_ing.py config.txt
"""

import random
import sys

from config_parser import ConfigError, MazeConfig, load_config
from maze_display import PATTERN_COLOURS, WALL_COLOURS, print_menu, show
from maze_writer import write_maze
from mazegen import MazeGenerator


def build_maze(config: MazeConfig, seed: int | None) -> MazeGenerator:
    """Create and generate a maze from the settings."""
    maze = MazeGenerator(
        width=config.width,
        height=config.height,
        entry=config.entry,
        exit=config.exit,
        seed=seed,
        perfect=config.perfect,
    )
    maze.generate()
    return maze


def save(maze: MazeGenerator, path: str) -> bool:
    """Write the output file. Print an error instead of crashing."""
    try:
        write_maze(maze, path)
    except OSError as error:
        print(
            f"Error: cannot write '{path}': {error.strerror}",
            file=sys.stderr,
        )
        return False
    return True


def run_menu(config: MazeConfig, maze: MazeGenerator) -> None:
    """Show the maze and handle the user choices until Quit."""
    session_rng = random.Random(config.seed)
    show_path: bool = False
    wall_idx: int = 0
    pattern_idx: int = 0
    message: str = ""

    while True:
        show(
            maze,
            show_path,
            WALL_COLOURS[wall_idx],
            PATTERN_COLOURS[pattern_idx],
        )
        print_menu()
        if message:
            print(message)
            message = ""

        try:
            choice = input("Choice? (1-5): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if choice == "1":
            try:
                new_seed = session_rng.randrange(2**32)
                maze = build_maze(config, new_seed)
            except ValueError as error:
                print(f"Error: {error}", file=sys.stderr)
                return
            save(maze, config.output_file)
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            wall_idx = (wall_idx + 1) % len(WALL_COLOURS)
        elif choice == "4":
            pattern_idx = (pattern_idx + 1) % len(PATTERN_COLOURS)
        elif choice == "5":
            return
        else:
            message = "Invalid choice: type a number from 1 to 5."


def main() -> int:
    """Run the main program flow."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        return 1

    try:
        config = load_config(sys.argv[1])
        maze = build_maze(config, config.seed)
        if not save(maze, config.output_file):
            return 1
        run_menu(config, maze)
    except ConfigError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
