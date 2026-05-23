import unittest
import numpy as np
from src.grid import Grid
from src.generator import GridGenerator

class TestGenerator(unittest.TestCase):
    def test_simple_density(self):
        grid = Grid(20, 20)
        GridGenerator.generate_simple(grid, density=0.25, seed=42)
        
        # Conta ostacoli fissi (state == 1)
        obstacles = np.sum(grid.state == 1)
        self.assertEqual(obstacles, 100)  # 20 * 20 * 0.25 = 100

    def test_cluster(self):
        grid = Grid(30, 30)
        GridGenerator.generate_cluster(grid, num_clusters=3, min_size=5, max_size=10, seed=123)
        obstacles = np.sum(grid.state == 1)
        self.assertTrue(15 <= obstacles <= 30)

    def test_diagonal(self):
        grid = Grid(20, 20)
        GridGenerator.generate_diagonal(grid, count=5, seed=77)
        obstacles = np.sum(grid.state == 1)
        self.assertTrue(10 <= obstacles <= 15)  # Coppie o triple per 5 volte

    def test_enclosure(self):
        grid = Grid(20, 20)
        GridGenerator.generate_enclosure(grid, count=2, min_side=4, max_side=6, seed=88)
        obstacles = np.sum(grid.state == 1)
        self.assertTrue(obstacles > 0)

    def test_bar(self):
        grid = Grid(20, 20)
        GridGenerator.generate_bar(grid, count=2, thickness=1, min_len=5, max_len=10, seed=99)
        obstacles = np.sum(grid.state == 1)
        # Una barra con varco ha ostacoli = length - 1 per barra
        self.assertTrue(obstacles > 0)

    def test_generate_grid_mix(self):
        types = ["simple", "cluster", "diagonal", "enclosure", "bar"]
        grid = GridGenerator.generate_grid(50, 50, types, density=0.2, seed=12345)
        self.assertEqual(grid.rows, 50)
        self.assertEqual(grid.cols, 50)
        obstacles = np.sum(grid.state == 1)
        # La densità finale dovrebbe essere vicina a 0.20
        final_density = obstacles / (50 * 50)
        self.assertTrue(0.15 <= final_density <= 0.25)
        
    def test_seed_reproducibility(self):
        grid1 = GridGenerator.generate_grid(30, 30, ["simple", "cluster"], density=0.2, seed=42)
        grid2 = GridGenerator.generate_grid(30, 30, ["simple", "cluster"], density=0.2, seed=42)
        
        self.assertTrue(np.array_equal(grid1.state, grid2.state))

if __name__ == "__main__":
    unittest.main()
