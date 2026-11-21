*This project has been created as part of the 42 curriculum by bbalci and alterzi.*

# A-Maze-ing

## Description

A-Maze-ing is a Python 3.10+ project that reads maze parameters from a
configuration file, generates customizable 2D mazes, exports them in a
hexadecimal wall-bitmask format, and renders an interactive colored view in
the terminal together with the shortest path from entry to exit.

The project is split into a reusable maze-generation library (`mazegen`) and
an interactive command-line application (`a_maze_ing.py`). Every maze contains
a solid "42" pattern made of fully closed cells, and the same `SEED` always
produces the same maze.

## Instructions

### Prerequisites

- Python 3.10 or newer
- `make`

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

- `make debug`: run the program under the Python debugger (`pdb`).
- `make lint`: run `flake8` and `mypy` checks with project flags.
- `make lint-strict`: run `flake8` and `mypy --strict`.
- `make test`: run the automated test suite (`pytest`).
- `make clean`: remove temporary caches and build artifacts.

### Configuration (config.txt)

Configuration files use a simple `KEY=VALUE` format. Empty lines and lines
starting with `#` are ignored.

| Key | Required | Description | Example |
|---|---|---|---|
| `WIDTH` | Yes | Maze width in cells (2–500) | `WIDTH=20` |
| `HEIGHT` | Yes | Maze height in cells (2–500) | `HEIGHT=15` |
| `ENTRY` | Yes | Entry coordinates `x,y` (0-indexed) | `ENTRY=0,0` |
| `EXIT` | Yes | Exit coordinates `x,y` (must differ from `ENTRY`) | `EXIT=19,14` |
| `OUTPUT_FILE` | Yes | Output file path for the hex maze export | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Yes | `True` for a single-path tree, `False` for loops (Pac-Man mode) | `PERFECT=True` |
| `SEED` | No | Integer seed for deterministic generation | `SEED=42` |

Coordinates start at `0,0` in the top-left corner (`x` is the column, `y` is
the row). `ENTRY` and `EXIT` must be inside the maze. A missing mandatory key
or an invalid value raises a `ConfigError` and the program exits with a clear
error message instead of a traceback.

Example `config.txt`:

```
# Default A-Maze-ing configuration
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

### Output File Format

The file written to `OUTPUT_FILE` contains:

1. One line per maze row, one hexadecimal digit per cell. Bit 0 = North,
   bit 1 = East, bit 2 = South, bit 3 = West; a set bit means the wall is
   closed (e.g. `D` = `1101`: only the east side is open, `F` = fully closed).
2. An empty line.
3. The entry coordinates `x,y`.
4. The exit coordinates `x,y`.
5. The shortest path from entry to exit using the letters `N`, `E`, `S`, `W`.

## Algorithms & Design Choices

### Maze Generation (Iterative DFS / Recursive Backtracker)

We chose an iterative Depth-First Search (DFS) with an explicit stack rather
than recursion:

1. Start with all walls closed; cells of the "42" pattern are marked as
   visited so they are never carved.
2. Push the entry cell on the stack.
3. Pick a random unvisited neighbour of the top cell, remove the wall between
   them and push the neighbour.
4. If there is no unvisited neighbour, pop the stack (backtrack).
5. Stop when the stack is empty.

Iterative DFS avoids Python's recursion depth limit on large grids, always
produces a fully connected spanning tree (`PERFECT=True`) with zero loops, and
gives reproducible output when `SEED` is set. It also creates long, winding
corridors that look like a real maze.

### Shortest Path Solver (BFS)

To compute the shortest path from `ENTRY` to `EXIT`, the generator uses
Breadth-First Search (BFS) with `collections.deque`. Because all maze steps
have equal weight, BFS guarantees the shortest path, returned as a sequence of
`N`, `E`, `S`, `W` moves.

### Non-Perfect Mode & "42" Pattern

- **"42" pattern**: when the maze is at least 9x7, a centered 7x5 solid "42"
  pattern (`15` = all walls closed) is reserved before carving. Placing
  `ENTRY` or `EXIT` inside this pattern raises a `ValueError`. Smaller mazes
  omit the pattern (`pattern_drawn=False`) and print a warning to `stderr`.
- **`PERFECT=False`**: additional walls are opened to create loops (at least
  two independent paths) and to reduce dead ends, while strictly forbidding
  3x3 completely open areas. Any wall opening that would break these rules is
  rolled back.

### Reusable Package (mazegen)

The core generation logic is decoupled into the standalone `mazegen` package,
distributed as a Python wheel (`mazegen-*.whl`) at the repository root. It
knows nothing about the config file, the terminal display or the output file.

- Build: `python3 -m build`, then copy the wheel from `dist/` to the repository
  root.
- Install: `pip install mazegen-*.whl`
- Main class: `MazeGenerator`
- Key attributes: `grid`, `entry`, `exit`, `solution`, `solution_cells`,
  `pattern_cells`, `pattern_drawn`, `seed`.

Detailed API examples and build instructions can be found in
`mazegen/README.md`.

## Team & Project Management

The project was developed collaboratively by two team members using feature
branches and Pull Request code reviews:

- **alterzi (Person A)**: core maze model (`mazegen/model.py`), generation and
  solving algorithms (`mazegen/generator.py`), algorithm unit tests
  (`tests/test_generator.py`), packaging (`pyproject.toml`, `LICENSE.md`,
  `mazegen/README.md`, `.whl`).
- **bbalci (Person B)**: repository setup (`.gitignore`, `.flake8`,
  `Makefile`, `config.txt`), configuration validation (`config_parser.py`),
  hex file writer (`maze_writer.py`), terminal display and menu
  (`maze_display.py`), main CLI (`a_maze_ing.py`) and the main `README.md`.

The work was split along the package boundary, so each member could develop
and test their part independently. What worked well: the clear separation
between library and application, and cross-reviewing each other's Pull
Requests. What could be improved: setting up the Makefile, linting and
packaging earlier in the project.

Tools: Git/GitHub, `flake8`, `mypy`, `pytest`, `pdb`, `build`.

## Resources

- [Jamis Buck — Maze Generation Algorithms](https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap)
- [Maze generation algorithm (Wikipedia)](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Breadth-first search (Wikipedia)](https://en.wikipedia.org/wiki/Breadth-first_search)
- Python 3 Official Documentation (`dataclasses`, `collections.deque`,
  `typing.Protocol`)
- [PEP 8](https://peps.python.org/pep-0008/) and
  [PEP 257](https://peps.python.org/pep-0257/)
- 42 School — A-Maze-ing Project Subject PDF

## AI Usage Disclosure

AI coding assistants were used during development as a learning and
productivity aid, specifically for:

- Step-by-step code walkthroughs and beginner-level concept explanations.
- Structuring error-handling patterns (`ConfigError`, `ValueError`,
  `OSError`).
- Drafting `pytest` unit test cases and formatting documentation.

All generated code and architectural decisions were reviewed, tested, and
understood by the team members before committing.