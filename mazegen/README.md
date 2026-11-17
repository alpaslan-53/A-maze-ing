# mazegen

A small, dependency-free maze generator written in pure Python (3.10+).

* Perfect mazes (one single path between any two cells) or playable
  mazes with loops and minimal dead-ends.
* A "42" pattern made of fully closed cells is drawn in the middle.
* Reproducible: the same seed always gives the same maze.
* Computes the shortest path between the entry and the exit.

## Installation

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

## Basic Example

```python
from mazegen import MazeGenerator

# 1. Instantiate the generator (width, height)
gen = MazeGenerator(width=20, height=15)

# 2. Build the maze structure and solve it
gen.generate()

# 3. Access the solution letters
print(gen.solution)  # e.g., "EESSWN..."
```

## Custom Parameters

```python
gen = MazeGenerator(
    width=30,          # number of columns (at least 2)
    height=20,         # number of rows (at least 2)
    entry=(0, 0),      # (x, y) start coordinate
    exit=(29, 19),     # (x, y) exit coordinate
    perfect=False,     # True: single path, False: Pac-Man board with loops
    seed=42,           # reproducible seed
)
gen.generate()
```

If the maze is smaller than 9x7, the "42" pattern is omitted and
`gen.pattern_drawn` is set to `False`.

## Accessing the Maze Structure

`gen.grid[y][x]` is an integer from 0 to 15 representing the walls of the cell
at row `y`, column `x`. A bit set to 1 means the wall is **closed**:

| Bit | Value | Wall  |
|-----|-------|-------|
| 0   | 1     | North |
| 1   | 2     | East  |
| 2   | 4     | South |
| 3   | 8     | West  |

Useful attributes:

* `gen.grid`: 2D list of wall bitmasks (`list[list[int]]`).
* `gen.pattern_cells`: Coordinates belonging to the "42" pattern (`set[Cell]`).
* `gen.pattern_drawn`: Whether the "42" pattern was drawn (`bool`).
* `gen.count_loops()`: Returns the number of independent loops.
* `gen.count_dead_ends()`: Returns the number of dead-end cells.

## Accessing the Solution

* `gen.solution`: Shortest path as direction letters (`str`, e.g., `"EESSW"`).
* `gen.solution_cells`: Path as coordinate sequence (`list[Cell]`).

## License

MIT License. See `LICENSE.md` for full terms.
