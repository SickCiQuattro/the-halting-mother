import unittest
import os
import tempfile
from src.grid import Grid, compute_components

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

    def test_save_load(self):
        grid = Grid(10, 10)
        grid.types = ["simple", "cluster"]
        grid.set_obstacle(1, 1)
        grid.set_obstacle(2, 2)
        grid.set_obstacle(3, 3)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "grid.json")
            grid.save(path)

            loaded = Grid.load(path)
            self.assertEqual(loaded.rows, 10)
            self.assertEqual(loaded.cols, 10)
            self.assertEqual(loaded.types, ["simple", "cluster"])
            self.assertFalse(loaded.is_traversable(1, 1))
            self.assertFalse(loaded.is_traversable(2, 2))
            self.assertTrue(loaded.is_traversable(0, 0))

    def test_compute_components_muro_divisorio(self):
        # Muro verticale completo in colonna 2: due componenti distinti, ostacoli a -1
        grid = Grid(5, 5)
        for r in range(5):
            grid.set_obstacle(r, 2)
        labels = compute_components(grid.state)

        self.assertEqual(labels[0, 0], labels[4, 1])   # Lato sinistro connesso
        self.assertEqual(labels[0, 3], labels[4, 4])   # Lato destro connesso
        self.assertNotEqual(labels[0, 0], labels[0, 3])  # I due lati sono separati
        for r in range(5):
            self.assertEqual(labels[r, 2], -1)         # Ostacoli etichettati -1

    def test_compute_components_passaggio_diagonale(self):
        # Due ostacoli che si toccano per lo spigolo NON separano le celle libere in
        # diagonale (pag. 3: attraversamento diagonale sempre ammesso)
        grid = Grid(2, 2)
        grid.set_obstacle(0, 1)
        grid.set_obstacle(1, 0)
        labels = compute_components(grid.state)
        self.assertEqual(labels[0, 0], labels[1, 1])

    def test_load_senza_tipologie(self):
        # I file JSON salvati prima dell'introduzione del campo "types" restano caricabili
        grid = Grid(5, 5)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "grid.json")
            grid.save(path)
            import json
            with open(path) as f:
                data = json.load(f)
            del data["types"]
            with open(path, "w") as f:
                json.dump(data, f)
            loaded = Grid.load(path)
            self.assertEqual(loaded.types, [])

if __name__ == "__main__":
    unittest.main()
