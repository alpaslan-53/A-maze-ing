"""A-Maze-ing main program and interactive terminal menu."""

import random
import sys

from config_parser import ConfigError, MazeConfig, load_config
from maze_display import PATTERN_COLOURS, WALL_COLOURS, print_menu, show
from maze_writer import write_maze
from mazegen import MazeGenerator


def generate_new_maze(
    config: MazeConfig, seed_number: int | None
) -> MazeGenerator:
    """Create and return a generated maze using config settings."""
    maze = MazeGenerator(
        width=config.width,
        height=config.height,
        entry=config.entry,
        exit=config.exit,
        seed=seed_number,
        perfect=config.perfect,
    )
    maze.generate()
    return maze


def save_to_file(maze: MazeGenerator, file_path: str) -> bool:
    """Write the maze to a file. Return False if writing fails."""
    try:
        write_maze(maze, file_path)
        return True
    except OSError as error:
        print(f"Error: cannot write '{file_path}': {error}", file=sys.stderr)
        return False


def open_menu(config: MazeConfig, maze: MazeGenerator) -> None:
    """Display the maze and handle user choices (1-5) in a loop."""
    show_solution: bool = False
    wall_index: int = 0
    pattern_index: int = 0
    error_message: str = ""

    while True:
        current_wall_color = WALL_COLOURS[wall_index]
        current_pattern_color = PATTERN_COLOURS[pattern_index]

        show(maze, show_solution, current_wall_color, current_pattern_color)
        print_menu()

        if error_message != "":
            print(error_message)
            error_message = ""

        try:
            choice = input("Choice? (1-5): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if choice == "1":
            try:
                random_seed = random.randint(1, 100000)
                maze = generate_new_maze(config, random_seed)
            except ValueError as error:
                print(f"Error: {error}", file=sys.stderr)
                return
            save_to_file(maze, config.output_file)

        elif choice == "2":
            if show_solution is True:
                show_solution = False
            else:
                show_solution = True

        elif choice == "3":
            wall_index = wall_index + 1
            if wall_index == len(WALL_COLOURS):
                wall_index = 0

        elif choice == "4":
            pattern_index = pattern_index + 1
            if pattern_index == len(PATTERN_COLOURS):
                pattern_index = 0

        elif choice == "5":
            return

        else:
            error_message = "Invalid choice: type a number from 1 to 5."


def main() -> int:
    """Start the program, catch any errors, and return an exit code."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        return 1

    config_file_path = sys.argv[1]

    try:
        config = load_config(config_file_path)
        maze = generate_new_maze(config, config.seed)
        if not save_to_file(maze, config.output_file):
            return 1
        open_menu(config, maze)
    except (ConfigError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
