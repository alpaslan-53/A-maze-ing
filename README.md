*This project has been created as part of the 42 curriculum by bbalci and alterzi.*

# A-Maze-ing

## Description

**A-Maze-ing** is a Python 3.10+ project that reads maze parameters from a
configuration file, generates customizable 2D mazes, exports them in a
hexadecimal wall-bitmask format, and renders an interactive colored view in the
terminal.

The project is split into a reusable maze-generation library (`mazegen`) and an
interactive command-line application (`a_maze_ing.py`).

## Instructions

### Prerequisites

* Python 3.10 or newer
* `make`

### Installation & Execution

```bash
# Install dependencies (flake8, mypy, pytest, etc.)
make install

# Generate and display the maze using the default config.txt
make run

# Or run manually with a custom config file
python3 a_maze_ing.py config.txt
```

### Other Makefile Targets

* `make debug`: Run the program under the Python debugger (`pdb`).
* `make lint`: Run `flake8` and `mypy` checks with project flags.
* `make lint-strict`: Run `flake8` and `mypy --strict`.
* `make test`: Run the automated test suite (`pytest`).
* `make clean`: Remove temporary caches and build artifacts.

## Configuration (`config.txt`)

Configuration files use a simple `KEY=VALUE` format. Empty lines and lines
starting with `#` are ignored.

| Key | Required | Description | Example |
| :--- | :---: | :--- | :--- |
| `WIDTH` | Yes | Maze width in cells (2–500) | `WIDTH=20` |
| `HEIGHT` | Yes | Maze height in cells (2–500) | `HEIGHT=15` |
| `ENTRY` | Yes | Entry coordinates `x,y` (0-indexed) | `ENTRY=0,0` |
| `EXIT` | Yes | Exit coordinates `x,y` (must differ from `ENTRY`) | `EXIT=19,14` |
| `OUTPUT_FILE` | Yes | Output file path for hex maze export | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Yes | `True` for single-path tree, `False` for loops (Pac-Man mode) | `PERFECT=True` |
| `SEED` | No | Integer seed for deterministic generation | `SEED=42` |

## Algorithms & Design Choices

### Maze Generation (Iterative DFS / Recursive Backtracker)
We chose an iterative Depth-First Search (DFS) with an explicit stack rather
than recursion. Iterative DFS avoids Python's recursion depth limit on large
grids while guaranteeing a fully connected spanning tree (`PERFECT=True`) with
zero loops and reproducible output when `SEED` is set.

### Shortest Path Solver (BFS)
To compute the shortest path from `ENTRY` to `EXIT`, the generator uses
Breadth-First Search (BFS) with `collections.deque`. Because all maze steps
have equal weight, BFS guarantees the shortest path (`N`, `E`, `S`, `W`).

### Non-Perfect Mode & "42" Pattern
* **42 Pattern:** When dimensions are at least `9x7`, a centered `7x5` solid
  `"42"` pattern (`15` = all walls closed) is reserved before carving. Placing
  `ENTRY` or `EXIT` inside this pattern raises a `ValueError`. Smaller mazes
  omit the pattern (`pattern_drawn=False`) and print a warning to `stderr`.
* **`PERFECT=False`:** Opens additional walls to create loops (at least two
  independent paths) and reduces dead ends while strictly forbidding `3x3`
  completely open areas.

## Reusable Package (`mazegen`)

The core generation logic is decoupled into the standalone `mazegen` package,
distributed as a Python wheel (`mazegen-*.whl`) at the repository root.

* **Main class:** `MazeGenerator`
* **Key attributes:** `grid`, `entry`, `exit`, `solution`, `solution_cells`,
  `pattern_cells`, `pattern_drawn`, `seed`.

*(Detailed API examples and build instructions can be found in
`mazegen/README.md` once package A5 is merged).*

## Team & Project Management

The project was developed collaboratively by two team members using feature
branches and Pull Request code reviews:

* **alterzi (Person A):** Core maze model (`mazegen/model.py`), generation &
  solving algorithms (`mazegen/generator.py`), algorithm unit tests
  (`tests/test_generator.py`), packaging (`pyproject.toml`, `LICENSE.md`,
  `mazegen/README.md`, `.whl`).
* **bbalci (Person B):** Repository setup (`.gitignore`, `.flake8`, `Makefile`,
  `config.txt`), configuration validation (`config_parser.py`), hex file writer
  (`maze_writer.py`), terminal display & menu (`maze_display.py`), main CLI
  (`a_maze_ing.py`), config/CLI tests (`tests/test_config_and_output.py`), and
  main `README.md`.

## AI Usage Disclosure

AI coding assistants were used during development as a learning and
productivity aid—specifically for:
* Step-by-step code walkthroughs and beginner-level concept explanations.
* Structuring error-handling patterns (`ConfigError`, `ValueError`, `OSError`).
* Drafting `pytest` unit test cases and formatting documentation.

All generated code and architectural decisions were reviewed, tested, and
understood by the team members before committing.

## Resources

* [Jamis Buck — Maze Generation Algorithms](https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap)
* [Python 3 Official Documentation (`dataclasses`, `collections.deque`, `typing.Protocol`)](https://docs.python.org/3/)
* 42 School — *A-Maze-ing* Project Subject PDF
