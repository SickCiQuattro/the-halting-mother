import unittest

from src.generator import GridGenerator
from src.experiment import ExperimentRunner


class TestExperimentSmoke(unittest.TestCase):
    """Rete di sicurezza minima per src/experiment.py, privo di prove unitarie proprie
    prima dello split in src/experiment_runner.py, src/experiment_plots.py e
    src/experiment_verifica.py: verifica solo le chiavi restituite, non l'implementazione."""

    CHIAVI_ATTESE = {
        "path_length", "landmarks_count", "landmarks", "timed_out",
        "elapsed_time_s", "peak_memory_kb", "frontier_cells",
        "pruning_false", "recursive_calls", "max_depth"
    }

    def _griglia(self):
        grid = GridGenerator.generate_grid(10, 10, ["simple"], density=0.1, seed=1)
        grid.clear_cell(0, 0)
        grid.clear_cell(9, 9)
        return grid

    def test_run_single_benchmark_chiavi(self):
        grid = self._griglia()
        risultato = ExperimentRunner.run_single_benchmark(grid, (0, 0), (9, 9), timeout=5.0)
        self.assertEqual(set(risultato.keys()), self.CHIAVI_ATTESE)
        self.assertFalse(risultato["timed_out"])
        self.assertLess(risultato["path_length"], float("inf"))

    def test_run_benchmark_coppia_simmetria(self):
        grid = self._griglia()
        risultato = ExperimentRunner.run_benchmark_coppia(grid, (0, 0), (9, 9), timeout=5.0)
        self.assertIn("andata", risultato)
        self.assertIn("ritorno", risultato)
        self.assertTrue(risultato["simmetria_verificabile"])
        self.assertTrue(risultato["simmetria_ok"])

    def test_verify_symmetry_chiavi(self):
        grid = self._griglia()
        risultati = ExperimentRunner.verify_symmetry(grid, [((0, 0), (9, 9))])
        self.assertEqual(len(risultati), 1)
        self.assertIn("symmetry_ok", risultati[0])
        self.assertTrue(risultati[0]["symmetry_ok"])


if __name__ == "__main__":
    unittest.main()
