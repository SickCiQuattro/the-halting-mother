import unittest
import numpy as np
from src.grid import Grid
from src.camminomin import camminomin, reconstruct_path, compact

class TestCamminomin(unittest.TestCase):
    def test_same_origin_dest(self):
        grid = Grid(5, 5)
        o = (2, 2)
        d = (2, 2)
        
        min_len, landmarks, timed_out = camminomin(o, d, grid.state)
        self.assertEqual(min_len, 0.0)
        self.assertEqual(landmarks, [(o, 0), (d, 1)])
        self.assertFalse(timed_out)

    def test_direct_reachability(self):
        grid = Grid(10, 10)
        o = (1, 1)
        d = (3, 5)  # dy=2, dx=4. dlib = 2*sqrt(2) + 2
        
        min_len, landmarks, timed_out = camminomin(o, d, grid.state)
        # Dovrebbe essere raggiungibile direttamente (in context)
        expected_len = 2.0 * np.sqrt(2.0) + 2.0
        self.assertAlmostEqual(min_len, expected_len)
        self.assertEqual(landmarks, [(o, 0), (d, 1)])

    def test_simple_barrier_pathfinding(self):
        grid = Grid(10, 10)
        # Crea un muro verticale in colonna 4, riga 0 a 7
        for r in range(8):
            grid.set_obstacle(r, 4)
            
        o = (3, 2)  # A sinistra del muro
        d = (3, 7)  # A destra del muro
        
        # O e D sono libere
        self.assertTrue(grid.is_traversable(o[0], o[1]))
        self.assertTrue(grid.is_traversable(d[0], d[1]))
        
        # Cerca cammino minimo
        min_len, landmarks, timed_out = camminomin(o, d, grid.state, use_strong_pruning=True)
        
        self.assertFalse(timed_out)
        self.assertTrue(min_len < float('inf'))
        self.assertTrue(len(landmarks) >= 3)  # O -> F -> D (o più landmark)
        
        # Ricostruisci il cammino completo di celle
        path = reconstruct_path(landmarks, grid.state)
        self.assertTrue(len(path) > 0)
        self.assertEqual(path[0], o)
        self.assertEqual(path[-1], d)
        
        # Verifica che il cammino non attraversi ostacoli
        for cell in path:
            self.assertEqual(grid.state[cell], 0)

    def test_unreachable(self):
        grid = Grid(5, 5)
        # Circonda (4,4) di ostacoli
        grid.set_obstacle(3, 3)
        grid.set_obstacle(3, 4)
        grid.set_obstacle(4, 3)
        
        o = (0, 0)
        d = (4, 4)
        
        min_len, landmarks, timed_out = camminomin(o, d, grid.state)
        self.assertEqual(min_len, float('inf'))
        self.assertEqual(len(landmarks), 0)

    def test_unreachable_component_check_immediato(self):
        # Recinto chiuso: il controllo dei componenti connessi ritorna infinito senza
        # avviare la ricerca ricorsiva (nessuna invocazione registrata nelle statistiche)
        grid = Grid(10, 10)
        for i in range(3, 8):
            grid.set_obstacle(3, i)
            grid.set_obstacle(7, i)
            grid.set_obstacle(i, 3)
            grid.set_obstacle(i, 7)

        o = (0, 0)   # Esterno al recinto
        d = (5, 5)   # Interno al recinto

        stats = {}
        min_len, landmarks, timed_out = camminomin(o, d, grid.state, stats=stats)
        self.assertEqual(min_len, float('inf'))
        self.assertEqual(len(landmarks), 0)
        self.assertFalse(timed_out)
        self.assertEqual(stats.get('recursive_calls', 0), 0)

        # Stesso esito (ma con ricerca completa) disattivando il controllo
        min_len_no_check, _, _ = camminomin(o, d, grid.state, use_component_check=False)
        self.assertEqual(min_len_no_check, float('inf'))

    def test_greedy_seed_stessa_lunghezza(self):
        # Su una griglia con ostacoli, l'innesco goloso deve produrre la stessa lunghezza
        # minima della ricerca senza innesco (mai peggiore, mai un falso ottimo).
        grid = Grid(10, 10)
        for r in range(8):
            grid.set_obstacle(r, 4)

        o = (3, 2)
        d = (3, 7)

        len_senza, _, to_senza = camminomin(o, d, grid.state.copy(), use_strong_pruning=True, greedy_seed=False)
        len_con, seq_con, to_con = camminomin(o, d, grid.state.copy(), use_strong_pruning=True, greedy_seed=True)

        self.assertFalse(to_senza)
        self.assertFalse(to_con)
        self.assertAlmostEqual(len_senza, len_con)
        self.assertEqual(seq_con[0], (o, 0))
        self.assertEqual(seq_con[-1][0], d)

    def test_greedy_seed_gia_ottimo_non_perde_la_sequenza(self):
        # Se la discesa golosa individua già il cammino minimo (griglia priva di ostacoli),
        # la potatura con disuguaglianza stretta non deve far perdere la sequenza: il
        # cammino goloso resta il valore di ritorno di default.
        grid = Grid(15, 15)
        o, d = (0, 0), (14, 14)

        min_len, landmarks, timed_out = camminomin(o, d, grid.state, use_strong_pruning=True, greedy_seed=True)

        self.assertFalse(timed_out)
        self.assertGreater(min_len, 0.0)
        self.assertEqual(landmarks[0], (o, 0))
        self.assertEqual(landmarks[-1][0], d)

    def test_greedy_seed_ripristina_la_griglia(self):
        grid = Grid(10, 10)
        for r in range(8):
            grid.set_obstacle(r, 4)
        original_state = grid.state.copy()

        camminomin((3, 2), (3, 7), grid.state, use_strong_pruning=True, greedy_seed=True)

        np.testing.assert_array_equal(grid.state, original_state)

    def test_compact(self):
        seq1 = [((0, 0), 0), ((3, 4), 1)]
        seq2 = [((3, 4), 0), ((10, 12), 2)]
        self.assertEqual(compact(seq1, seq2), [((0, 0), 0), ((3, 4), 1), ((10, 12), 2)])

    def test_grid_state_restored_after_search(self):
        grid = Grid(10, 10)
        for r in range(8):
            grid.set_obstacle(r, 4)
        original_state = grid.state.copy()

        o = (3, 2)
        d = (3, 7)
        camminomin(o, d, grid.state, use_strong_pruning=True)

        np.testing.assert_array_equal(grid.state, original_state)

    def test_symmetry(self):
        grid = Grid(10, 10)
        # Crea qualche ostacolo sparso
        for r, c in [(2,2), (3,2), (4,2), (5,5), (6,5), (7,5)]:
            grid.set_obstacle(r, c)
            
        o = (1, 1)
        d = (8, 8)
        
        # O -> D
        len_od, landmarks_od, _ = camminomin(o, d, grid.state, use_strong_pruning=True)
        # D -> O
        len_do, landmarks_do, _ = camminomin(d, o, grid.state, use_strong_pruning=True)
        
        if len_od < float('inf') or len_do < float('inf'):
            self.assertAlmostEqual(len_od, len_do)

if __name__ == "__main__":
    unittest.main()
