import unittest
import numpy as np
import math
from src.grid import Grid
from src.free_paths import (
    dlib,
    get_diag_direction,
    free_path_type1,
    free_path_type2,
    compute_context_rays,
    compute_complement_rays,
    compute_frontier
)

class TestFreePaths(unittest.TestCase):
    def test_dlib(self):
        # O e D coincidenti
        self.assertEqual(dlib((0, 0), (0, 0)), 0.0)
        # Orizzontale puro: (0,0) -> (0,5). dy=0, dx=5. dlib = 5.0
        self.assertEqual(dlib((0, 0), (0, 5)), 5.0)
        # Verticale puro: (0,0) -> (4,0). dy=4, dx=0. dlib = 4.0
        self.assertEqual(dlib((0, 0), (4, 0)), 4.0)
        # Diagonale pura: (0,0) -> (3,3). dy=3, dx=3. dlib = 3 * sqrt(2)
        self.assertAlmostEqual(dlib((0, 0), (3, 3)), 3.0 * math.sqrt(2.0))
        # Quadrante I (generico): (5,5) -> (2,8). dy=3, dx=3. dlib = 3 * sqrt(2)
        # (5,5) -> (1,8). dy=4, dx=3. d_min=3, d_max=4. dlib = 3 * sqrt(2) + 1.0
        self.assertAlmostEqual(dlib((5, 5), (1, 8)), 3.0 * math.sqrt(2.0) + 1.0)

    def test_get_diag_direction(self):
        self.assertEqual(get_diag_direction((5, 5), (2, 8)), (-1, 1))  # NE
        self.assertEqual(get_diag_direction((5, 5), (2, 2)), (-1, -1)) # NW
        self.assertEqual(get_diag_direction((5, 5), (8, 2)), (1, -1))  # SW
        self.assertEqual(get_diag_direction((5, 5), (8, 8)), (1, 1))   # SE

    def test_free_paths_empty_grid(self):
        grid = Grid(10, 10)
        # In griglia vuota, tutti i cammini ideali dovrebbero esistere
        o = (3, 3)
        d = (6, 8)  # dy=3, dx=5.
        
        path1 = free_path_type1(o, d, grid.state)
        self.assertIsNotNone(path1)
        self.assertEqual(path1[0], o)
        self.assertEqual(path1[-1], d)
        # Lunghezza del cammino come nodi: 1 + d_max = 6 nodi
        self.assertEqual(len(path1), 6)
        
        path2 = free_path_type2(o, d, grid.state)
        self.assertIsNotNone(path2)
        self.assertEqual(path2[0], o)
        self.assertEqual(path2[-1], d)
        self.assertEqual(len(path2), 6)

    def test_free_paths_with_obstacle(self):
        grid = Grid(5, 5)
        o = (0, 0)
        d = (2, 2)  # pura diag
        
        # Metti ostacolo sulla diagonale in (1,1)
        grid.set_obstacle(1, 1)
        path1 = free_path_type1(o, d, grid.state)
        self.assertIsNone(path1)  # Diagonale bloccata

    def test_ray_casting_context_and_complement(self):
        grid = Grid(5, 5)
        o = (2, 2)
        
        # In griglia vuota, ray-casting da (2,2) dovrebbe coprire molte celle
        context = compute_context_rays(o, grid.state)
        self.assertIn((2, 2), context)
        self.assertIn((0, 0), context)  # Raggiungibile in diagonale pura (tipo 1)
        self.assertIn((2, 4), context)  # Raggiungibile in orizzontale puro
        
        complement = compute_complement_rays(o, grid.state, context)
        # Nessun elemento di complement dovrebbe essere in context
        self.assertEqual(len(context & complement), 0)
        
        # Le celle d'angolo come (0,1) non sono sulla diagonale né sugli assi.
        # Sono raggiungibili tramite tipo 2 o tipo 1?
        # (2,2) -> (0,1): dy=2, dx=1.
        # Tipo 1: diag (1 step NE -> (1,3)), poi card (verticale -> (0,3)? No, D è (0,1)).
        # Aspetta. (2,2) -> (0,1). dr=-1, dc=-1. dy=2, dx=1. d_min=1.
        # Tipo 1: diag prima. dr=-1, dc=-1. 1 step -> (1,1). Poi card: dy > dx, quindi vertical: dr=-1, dc=0. 1 step -> (0,1).
        # Quindi (0,1) è in context (raggiungibile con tipo 1).
        self.assertIn((0, 1), context)

        # Cosa c'è in complement?
        # Ad esempio, in griglia 5x5 da (2,2):
        # Proviamo (2,2) -> (0,3). dr=-1, dc=1. dy=2, dx=1. d_min=1.
        # Tipo 1: diag prima. dr=-1, dc=1. 1 step -> (1,3). Poi card vertical: dr=-1, dc=0. 1 step -> (0,3). Reachable with Type 1!
        # Tipo 2: card prima (vertical -> 1 step -> (1,2)), poi diag (1 step NE -> (0,3)). Reachable with Type 2!
        # Siccome è reachable con tipo 1, appartiene a context e quindi non è in complement.
        # Esiste una cella raggiungibile solo con Tipo 2 e non con Tipo 1 in griglia vuota?
        # No, in griglia completamente vuota, per qualsiasi cella, sia tipo 1 che tipo 2 sono liberi!
        # Quindi complement è vuoto in griglia vuota, perché context contiene già tutte le celle raggiungibili.
        self.assertEqual(len(complement), 0)

    def test_frontier(self):
        grid = Grid(5, 5)
        # Mettiamo un muro orizzontale in riga 1 con un varco in (1,2)
        grid.set_obstacle(1, 0)
        grid.set_obstacle(1, 1)
        grid.set_obstacle(1, 3)
        grid.set_obstacle(1, 4)
        
        o = (3, 2)  # Sotto la barriera
        
        context = compute_context_rays(o, grid.state)
        complement = compute_complement_rays(o, grid.state, context)
        frontier = compute_frontier(context, complement, grid.state)
        
        # Ci dovrebbero essere celle di frontiera
        self.assertTrue(len(frontier) > 0)
        
        # Tutte le celle in frontiera appartengono a context o complement
        closure = context | complement
        for cell, tipo in frontier:
            self.assertIn(cell, closure)

if __name__ == "__main__":
    unittest.main()
