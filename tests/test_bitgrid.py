import unittest
import numpy as np
from src.generator import GridGenerator
from src.bitgrid import BitPackedGrid
from src.free_paths import compute_context_rays, compute_complement_rays, compute_frontier
from src.camminomin import camminomin


class TestBitPackedGrid(unittest.TestCase):
    def test_accesso_e_assegnazione(self):
        grid = BitPackedGrid(4, 10)
        self.assertEqual(grid.shape, (4, 10))
        self.assertEqual(grid[2, 9], 0)
        grid[2, 9] = 1
        self.assertEqual(grid[2, 9], 1)
        grid[2, 9] = 2
        self.assertEqual(grid[2, 9], 2)
        grid[2, 9] = 0
        self.assertEqual(grid[2, 9], 0)
        with self.assertRaises(ValueError):
            grid[0, 0] = 3

    def test_copy_indipendente(self):
        grid = BitPackedGrid(3, 3)
        grid[1, 1] = 1
        copia = grid.copy()
        copia[1, 1] = 0
        self.assertEqual(grid[1, 1], 1)
        self.assertEqual(copia[1, 1], 0)

    def test_occupazione_memoria(self):
        # 2 bit/cella contro 8 bit/cella: i piani impacchettati occupano ~1/4
        size = 64
        grid = GridGenerator.generate_grid(size, size, ["simple"], density=0.2, seed=7)
        bit_grid = BitPackedGrid.from_array(grid.state)
        self.assertEqual(bit_grid.nbytes, grid.state.nbytes // 4)

    def test_equivalenza_round_trip(self):
        grid = GridGenerator.generate_grid(13, 21, ["simple", "cluster"], density=0.25, seed=3)
        bit_grid = BitPackedGrid.from_array(grid.state)
        np.testing.assert_array_equal(bit_grid.to_array(), grid.state)

    def test_equivalenza_chiusura_e_camminomin(self):
        # Gli algoritmi esistenti devono produrre risultati identici sulla matrice uint8
        # e sull'oggetto impacchettato (stessa interfaccia duck-typed)
        for seed in range(5):
            grid = GridGenerator.generate_grid(12, 12, ["simple", "cluster"], density=0.2, seed=seed)
            bit_grid = BitPackedGrid.from_array(grid.state)

            libere = [tuple(map(int, cella)) for cella in np.argwhere(grid.state == 0)]
            o, d = libere[0], libere[-1]

            context_u8 = compute_context_rays(o, grid.state)
            context_bit = compute_context_rays(o, bit_grid)
            self.assertEqual(context_u8, context_bit, f"seed={seed}")

            complement_u8 = compute_complement_rays(o, grid.state, context_u8)
            complement_bit = compute_complement_rays(o, bit_grid, context_bit)
            self.assertEqual(complement_u8, complement_bit, f"seed={seed}")

            frontier_u8 = compute_frontier(context_u8, complement_u8, grid.state)
            frontier_bit = compute_frontier(context_bit, complement_bit, bit_grid)
            self.assertEqual(sorted(frontier_u8), sorted(frontier_bit), f"seed={seed}")

            len_u8, seq_u8, _ = camminomin(o, d, grid.state.copy(), use_strong_pruning=True)
            len_bit, seq_bit, _ = camminomin(o, d, bit_grid.copy(), use_strong_pruning=True)
            self.assertEqual(len_u8, len_bit, f"seed={seed}")
            self.assertEqual(seq_u8, seq_bit, f"seed={seed}")


if __name__ == "__main__":
    unittest.main()
