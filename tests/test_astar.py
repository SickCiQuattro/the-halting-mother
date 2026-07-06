import unittest
import numpy as np
from src.grid import Grid
from src.generator import GridGenerator
from src.astar import astar
from src.camminomin import camminomin
from src.free_paths import dlib


class TestAstar(unittest.TestCase):
    def test_stesso_origine_destinazione(self):
        grid = Grid(5, 5)
        self.assertEqual(astar((2, 2), (2, 2), grid.state), 0.0)

    def test_linea_retta_griglia_vuota(self):
        grid = Grid(10, 10)
        o, d = (1, 1), (3, 5)
        self.assertAlmostEqual(astar(o, d, grid.state), dlib(o, d), places=9)

    def test_irraggiungibile(self):
        grid = Grid(5, 5)
        grid.set_obstacle(3, 3)
        grid.set_obstacle(3, 4)
        grid.set_obstacle(4, 3)
        self.assertEqual(astar((0, 0), (4, 4), grid.state), float('inf'))

    def test_destinazione_su_ostacolo(self):
        grid = Grid(5, 5)
        grid.set_obstacle(2, 2)
        self.assertEqual(astar((0, 0), (2, 2), grid.state), float('inf'))

    def test_taglio_angolo_ammesso(self):
        # Pag. 3: il passo diagonale fra celle libere è ammesso anche se due ostacoli
        # si toccano per lo spigolo. A* deve avere la stessa semantica dei cammini liberi.
        grid = Grid(2, 2)
        grid.set_obstacle(0, 1)
        grid.set_obstacle(1, 0)
        self.assertAlmostEqual(astar((0, 0), (1, 1), grid.state), np.sqrt(2.0), places=9)

    def test_equivalenza_con_camminomin(self):
        # Proprietà di equivalenza: su griglie casuali piccole di tipologie miste la
        # lunghezza di A* deve coincidere con quella di CAMMINOMIN (oracolo di correttezza),
        # inclusi i casi irraggiungibili.
        tipologie = [["simple"], ["cluster"], ["bar"], ["enclosure"], ["simple", "cluster"]]
        rng = np.random.default_rng(4242)
        confronti = 0

        for seed in range(20):
            tipi = tipologie[seed % len(tipologie)]
            grid = GridGenerator.generate_grid(15, 15, tipi, density=0.2, seed=seed)

            libere = [tuple(map(int, cella)) for cella in np.argwhere(grid.state == 0)]
            if len(libere) < 2:
                continue
            o, d = (libere[i] for i in rng.choice(len(libere), size=2, replace=False))

            len_astar = astar(o, d, grid.state)
            len_cm, _, timed_out = camminomin(
                o, d, grid.state.copy(), use_strong_pruning=True
            )
            self.assertFalse(timed_out)
            if len_astar == float('inf'):
                self.assertEqual(len_cm, float('inf'), f"seed={seed} O={o} D={d}")
            else:
                self.assertAlmostEqual(len_cm, len_astar, places=9, msg=f"seed={seed} O={o} D={d}")
            confronti += 1

        self.assertGreaterEqual(confronti, 15)


if __name__ == "__main__":
    unittest.main()
