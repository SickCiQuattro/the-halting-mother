import json
import os
import subprocess
import sys
import tempfile
import unittest

RADICE = os.path.join(os.path.dirname(__file__), "..")


class TestCli(unittest.TestCase):
    def _esegui(self, *argomenti: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, os.path.join(RADICE, "main.py"), *argomenti],
            capture_output=True, text=True, cwd=RADICE, check=False
        )

    def test_genera_e_risolve(self):
        with tempfile.TemporaryDirectory() as tmp:
            griglia = os.path.join(tmp, "g.json")
            gen = self._esegui("generate", "--rows", "12", "--cols", "12", "--seed", "1", "-o", griglia)
            self.assertEqual(gen.returncode, 0, gen.stderr)

            ris = self._esegui(
                "camminomin", "--grid", griglia, "--origin", "0,0", "--dest", "11,11", "--summary"
            )
            self.assertEqual(ris.returncode, 0, ris.stderr)
            self.assertIn("{", ris.stdout)
            json.loads(ris.stdout[ris.stdout.index("{"):ris.stdout.rindex("}") + 1])

    def test_griglia_inesistente(self):
        ris = self._esegui("camminomin", "--grid", "non_esiste.json", "--origin", "0,0", "--dest", "1,1")
        self.assertEqual(ris.returncode, 1)


if __name__ == "__main__":
    unittest.main()
