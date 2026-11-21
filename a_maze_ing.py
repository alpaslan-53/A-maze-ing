"""A-Maze-ing application runner and interactive console interface.

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
    """Instantiate and construct a maze instance using the provided config."""
    generator = MazeGenerator(
        width=config.width,
        height=config.height,
        entry=config.entry,
        exit=config.exit,
        seed=seed,
        perfect=config.perfect,
    )
    generator.generate()
    return generator


def save(maze: MazeGenerator, path: str) -> bool:
    """Safely persist the maze to file without raising fatal exceptions."""
    try:
        write_maze(maze, path)
    except OSError as err:
        print(
            f"Error: cannot write '{path}': {err.strerror}",
            file=sys.stderr,
        )
        return False
    return True


def run_menu(config: MazeConfig, maze: MazeGenerator) -> None:
    """Handle interactive terminal navigation and user commands."""
    rng = random.Random(config.seed)
    display_path: bool = False
    wall_color_idx: int = 0
    pattern_color_idx: int = 0
    notice: str = ""

    while True:
        show(
            maze,
            display_path,
            WALL_COLOURS[wall_color_idx],
            PATTERN_COLOURS[pattern_color_idx],
        )
        print_menu()
        if notice:
            print(notice)
            notice = ""

        try:
            user_input = input("Choice? (1-5): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if user_input == "1":
            try:
                next_seed = rng.randrange(2**32)
                maze = build_maze(config, next_seed)
            except ValueError as err:
                print(f"Error: {err}", file=sys.stderr)
                return
            save(maze, config.output_file)
        elif user_input == "2":
            display_path = not display_path
        elif user_input == "3":
            wall_color_idx = (wall_color_idx + 1) % len(WALL_COLOURS)
        elif user_input == "4":
            pattern_color_idx = (pattern_color_idx + 1) % len(PATTERN_COLOURS)
        elif user_input == "5":
            return
        else:
            notice = "Invalid choice: type a number from 1 to 5."


def main() -> int:
    """Parse CLI arguments, initialize maze state, and launch UI loop."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        return 1

    try:
        settings = load_config(sys.argv[1])
        active_maze = build_maze(settings, settings.seed)
        if not save(active_maze, settings.output_file):
            return 1
        run_menu(settings, active_maze)
    except ConfigError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
