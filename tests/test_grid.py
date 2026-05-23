import unittest
import os
import tempfile
from src.grid import Grid

class TestGrid(unittest.TestCase):
    def test_creation(self):
        grid = Grid(10, 15)
        self.assertEqual(grid.rows, 10)
        self.assertEqual(grid.cols, 15)
        self.assertTrue(grid.is_traversable(5, 5))
        self.assertFalse(grid.is_traversable(10, 15))  # Fuori limiti

    def test_obstacles(self):
        grid = Grid(5, 5)
        grid.set_obstacle(2, 3)
        self.assertFalse(grid.is_traversable(2, 3))
        self.assertEqual(grid.state[2, 3], 1)
        grid.clear_cell(2, 3)
        self.assertTrue(grid.is_traversable(2, 3))
        self.assertEqual(grid.state[2, 3], 0)

    def test_neighbors(self):
        grid = Grid(3, 3)
        # Angolo: (0, 0) dovrebbe avere 3 vicini in griglia vuota
        n_00 = grid.neighbors(0, 0)
        self.assertEqual(len(n_00), 3)
        self.assertIn((0, 1), n_00)
        self.assertIn((1, 0), n_00)
        self.assertIn((1, 1), n_00)
        
        # Centro: (1, 1) dovrebbe avere 8 vicini
        n_11 = grid.neighbors(1, 1)
        self.assertEqual(len(n_11), 8)
        
        # Imposta ostacoli
        grid.set_obstacle(0, 1)
        n_00_obs = grid.neighbors(0, 0)
        self.assertEqual(len(n_00_obs), 2)  # (0, 1) è ostacolo ora
        self.assertNotIn((0, 1), n_00_obs)

    def test_backtracking_marks(self):
        grid = Grid(5, 5)
        cells = [(1, 1), (1, 2), (2, 2)]
        grid.mark_temp(cells, depth_id=3)
        
        for r, c in cells:
            self.assertFalse(grid.is_traversable(r, c))
            self.assertEqual(grid.state[r, c], 3)
            
        grid.unmark_temp(cells)
        for r, c in cells:
            self.assertTrue(grid.is_traversable(r, c))
            self.assertEqual(grid.state[r, c], 0)

    def test_save_load(self):
        grid = Grid(10, 10)
        grid.set_obstacle(1, 1)
        grid.set_obstacle(2, 2)
        grid.set_obstacle(3, 3)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "grid.json")
            grid.save(path)
            
            loaded = Grid.load(path)
            self.assertEqual(loaded.rows, 10)
            self.assertEqual(loaded.cols, 10)
            self.assertFalse(loaded.is_traversable(1, 1))
            self.assertFalse(loaded.is_traversable(2, 2))
            self.assertTrue(loaded.is_traversable(0, 0))

if __name__ == "__main__":
    unittest.main()
