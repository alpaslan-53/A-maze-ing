"""Unit tests for mazegen.MazeGenerator matching subject requirements."""

from collections import deque
import unittest

from mazegen import DIRECTIONS, EAST, SOUTH, MazeGenerator

Cell = tuple[int, int]


class TestMazeGenerator(unittest.TestCase):
    """Test suite covering connectivity, loops, coherence, seed and rules."""

    def _reachable_cells(self, gen: MazeGenerator) -> set[Cell]:
        """Return all cells reachable from entry using BFS traversal."""
        visited: set[Cell] = {gen.entry}
        queue: deque[Cell] = deque([gen.entry])
        while queue:
            cx, cy = queue.popleft()
            for d in DIRECTIONS:
                if not (gen.grid[cy][cx] & d.bit):
                    nx: int = cx + d.dx
                    ny: int = cy + d.dy
                    if (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
        return visited

    def _assert_common_rules(self, gen: MazeGenerator) -> None:
        """Verify universal subject rules: bounds, borders, coherence."""
        w, h = gen.width, gen.height

        # 1. External borders must be closed & cells in range [0, 15]
        for y in range(h):
            for x in range(w):
                val = gen.grid[y][x]
                self.assertTrue(0 <= val <= 15)
                if y == 0:
                    self.assertTrue(bool(val & 1))
                if x == w - 1:
                    self.assertTrue(bool(val & 2))
                if y == h - 1:
                    self.assertTrue(bool(val & 4))
                if x == 0:
                    self.assertTrue(bool(val & 8))

                # 2. Coherence: neighboring cells share identical wall state
                if x + 1 < w:
                    self.assertEqual(
                        bool(val & 2),
                        bool(gen.grid[y][x + 1] & 8),
                    )
                if y + 1 < h:
                    self.assertEqual(
                        bool(val & 4),
                        bool(gen.grid[y + 1][x] & 1),
                    )

        # 3. 42 pattern cells must be fully closed (15)
        for px, py in gen.pattern_cells:
            self.assertEqual(gen.grid[py][px], 15)

        # 4. Full connectivity: all non-pattern cells are reachable
        reachable = self._reachable_cells(gen)
        expected_cells = w * h - len(gen.pattern_cells)
        self.assertEqual(len(reachable), expected_cells)

        # 5. No 3x3 open area anywhere in the maze
        for by in range(h - 2):
            for bx in range(w - 2):
                self.assertFalse(gen._block_is_open(bx, by))

    def test_perfect_maze(self) -> None:
        """Verify PERFECT=True generates a tree with exactly 0 loops."""
        gen = MazeGenerator(width=15, height=11, perfect=True, seed=42)
        gen.generate()
        self._assert_common_rules(gen)
        self.assertEqual(gen.count_loops(), 0)
        self.assertTrue(len(gen.solution) > 0)

    def test_non_perfect_maze(self) -> None:
        """Verify PERFECT=False creates >= 2 loops and minimal dead-ends."""
        gen = MazeGenerator(width=20, height=15, perfect=False, seed=42)
        gen.generate()
        self._assert_common_rules(gen)
        self.assertGreaterEqual(gen.count_loops(), 2)
        # Dead-ends are reduced to pattern boundary pockets
        self.assertLessEqual(gen.count_dead_ends(), 3)

    def test_seed_reproducibility(self) -> None:
        """Verify identical seed produces identical maze and solution."""
        g1 = MazeGenerator(12, 10, seed=123).generate()
        g2 = MazeGenerator(12, 10, seed=123).generate()
        self.assertEqual(g1.grid, g2.grid)
        self.assertEqual(g1.solution, g2.solution)
        self.assertEqual(g1.solution_cells, g2.solution_cells)

    def test_different_seeds_produce_different_mazes(self) -> None:
        """Verify different seeds produce different maze structures."""
        g1 = MazeGenerator(12, 10, seed=101).generate()
        g2 = MazeGenerator(12, 10, seed=202).generate()
        self.assertNotEqual(g1.grid, g2.grid)

    def test_solution_path_traversal(self) -> None:
        """Verify solution string traces unbroken path from entry to exit."""
        gen = MazeGenerator(width=16, height=12, seed=77).generate()
        curr = gen.entry
        dir_map = {d.name: d for d in DIRECTIONS}

        for char in gen.solution:
            d = dir_map[char]
            cx, cy = curr
            self.assertFalse(bool(gen.grid[cy][cx] & d.bit))
            curr = (cx + d.dx, cy + d.dy)

        self.assertEqual(curr, gen.exit)
        self.assertEqual(gen.solution_cells[0], gen.entry)
        self.assertEqual(gen.solution_cells[-1], gen.exit)

    def test_small_maze_omits_pattern(self) -> None:
        """Verify mazes smaller than 9x7 gracefully omit the 42 pattern."""
        small = MazeGenerator(width=8, height=6, seed=1).generate()
        self.assertFalse(small.pattern_drawn)
        self.assertEqual(len(small.pattern_cells), 0)

        normal = MazeGenerator(width=9, height=7, seed=1).generate()
        self.assertTrue(normal.pattern_drawn)
        self.assertGreater(len(normal.pattern_cells), 0)

    def test_parameter_validations(self) -> None:
        """Verify invalid maze parameters raise explicit ValueError."""
        with self.assertRaises(ValueError):
            MazeGenerator(width=1, height=5)
        with self.assertRaises(ValueError):
            MazeGenerator(width=5, height=1)
        with self.assertRaises(ValueError):
            MazeGenerator(width=10, height=10, entry=(0, 0), exit=(0, 0))
        with self.assertRaises(ValueError):
            MazeGenerator(width=10, height=10, entry=(-1, 0))
        with self.assertRaises(ValueError):
            MazeGenerator(width=10, height=10, exit=(10, 5))

    def test_entry_inside_pattern_raises_error(self) -> None:
        """Verify entry inside 42 pattern raises ValueError during generate."""
        gen = MazeGenerator(width=15, height=11, entry=(4, 3))
        with self.assertRaises(ValueError):
            gen.generate()


if __name__ == "__main__":
    unittest.main()
