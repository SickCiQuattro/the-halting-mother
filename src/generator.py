import random
import logging
import numpy as np
from typing import List, Optional
from src.grid import Grid, Coordinate, NEIGHBORS_8

# Configura il logging standard per il modulo
logger = logging.getLogger(__name__)

class GridGenerator:
    """
    Generatore strategico ed estendibile di ostacoli per griglie bidimensionali.

    Supporta 5 tipologie distinte di ostacoli (Compito 1 dell'elaborato):
      1. simple: Ostacoli a singola cella sparsi in modo casuale con densità controllata.
      2. cluster: Agglomerati di celle ostacolo contigue mediante random walk da semi.
      3. diagonal: Ostacoli allineati diagonalmente (coppie o triple che si toccano per l'angolo).
      4. enclosure: Recinti rettangolari chiusi composti da ostacoli sui bordi.
      5. bar: Segmenti continui (orizzontali o verticali) con varchi casuali.
    """
    
    @staticmethod
    def _get_rng(seed: Optional[int]) -> random.Random:
        """Ritorna un'istanza isolata di Random pre-seminata per garantire riproducibilità totale."""
        return random.Random(seed) if seed is not None else random.Random()

    @staticmethod
    def _celle_libere(grid: Grid) -> list[Coordinate]:
        """Ritorna tutte le celle attualmente libere (stato 0) della griglia."""
        return [
            (r, c) for r in range(grid.rows) for c in range(grid.cols)
            if grid.state[r, c] == 0
        ]

    @classmethod
    def generate_simple(cls, grid: Grid, density: float, seed: Optional[int] = None) -> None:
        """
        Genera ostacoli sparsi a cella singola.
        
        La densità indica la frazione di celle della griglia da occupare.

        Args:
            grid: L'oggetto Griglia su cui operare.
            density: Densità target degli ostacoli (valore tra 0.0 e 1.0).
            seed: Seme casuale opzionale.
        """
        if not (0.0 <= density <= 1.0):
            raise ValueError(f"La densità deve essere compresa tra 0.0 e 1.0. Ricevuta: {density}")

        rng = cls._get_rng(seed)
        total_cells = grid.rows * grid.cols
        num_obstacles = int(total_cells * density)
        
        # Individua tutte le celle libere
        free_cells = cls._celle_libere(grid)

        if len(free_cells) < num_obstacles:
            num_obstacles = len(free_cells)
            
        chosen = rng.sample(free_cells, num_obstacles)
        for r, c in chosen:
            grid.set_obstacle(r, c)

    @classmethod
    def generate_cluster(
        cls, 
        grid: Grid, 
        num_clusters: int, 
        min_size: int, 
        max_size: int, 
        seed: Optional[int] = None
    ) -> None:
        """
        Genera agglomerati densi (cluster) di ostacoli contigui tramite cammino casuale a partire da semi.

        Args:
            grid: L'oggetto Griglia su cui operare.
            num_clusters: Numero di agglomerati distinti da generare.
            min_size: Dimensione minima (in celle) di ciascun cluster.
            max_size: Dimensione massima (in celle) di ciascun cluster.
            seed: Seme casuale opzionale.
        """
        if num_clusters < 0 or min_size <= 0 or max_size < min_size:
            raise ValueError("I parametri di clusterizzazione forniti non sono coerenti o validi.")

        rng = cls._get_rng(seed)
        
        for _ in range(num_clusters):
            free_cells = cls._celle_libere(grid)
            if not free_cells:
                break
            
            seme = rng.choice(free_cells)
            cluster_size = rng.randint(min_size, max_size)
            
            queue = [seme]
            visited = set()
            count = 0
            
            while queue and count < cluster_size:
                curr = rng.choice(queue)
                queue.remove(curr)
                
                if curr in visited:
                    continue
                
                grid.set_obstacle(curr[0], curr[1])
                visited.add(curr)
                count += 1
                
                # Aggiungi vicini non ancora ostacoli fisici
                r, c = curr
                for dr, dc in NEIGHBORS_8:
                    nr, nc = r + dr, c + dc
                    if grid.is_valid(nr, nc) and grid.state[nr, nc] == 0 and (nr, nc) not in visited:
                        queue.append((nr, nc))

    @classmethod
    def generate_diagonal(cls, grid: Grid, count: int, seed: Optional[int] = None) -> None:
        """
        Genera coppie o triple di ostacoli disposti unicamente in allineamento diagonale.
        Questa disposizione è cruciale per testare l'attraversamento dello spigolo.

        Args:
            grid: L'oggetto Griglia su cui operare.
            count: Numero totale di formazioni diagonali da tentare.
            seed: Seme casuale opzionale.
        """
        if count < 0:
            raise ValueError("Il parametro count deve essere positivo.")

        rng = cls._get_rng(seed)
        
        for _ in range(count):
            free_cells = cls._celle_libere(grid)
            if not free_cells:
                break
                
            r, c = rng.choice(free_cells)
            length = rng.choice([2, 3])  # Lunghezza di 2 o 3 celle diagonali
            diag_r = rng.choice([-1, 1])
            diag_c = rng.choice([-1, 1])
            
            for step in range(length):
                nr, nc = r + step * diag_r, c + step * diag_c
                if grid.is_valid(nr, nc):
                    grid.set_obstacle(nr, nc)

    @classmethod
    def generate_enclosure(
        cls, 
        grid: Grid, 
        count: int, 
        min_side: int, 
        max_side: int, 
        seed: Optional[int] = None
    ) -> None:
        """
        Genera recinti rettangolari (bordi di ostacoli e area interna libera da ostacoli fisici).

        Args:
            grid: L'oggetto Griglia su cui operare.
            count: Numero di recinti da tentare.
            min_side: Lunghezza minima del lato del recinto.
            max_side: Lunghezza massima del lato del recinto.
            seed: Seme casuale opzionale.
        """
        if count < 0 or min_side < 2 or max_side < min_side:
            raise ValueError("Parametri del recinto non validi.")

        rng = cls._get_rng(seed)
        
        for _ in range(count):
            w = rng.randint(min_side, max_side)
            h = rng.randint(min_side, max_side)
            
            if w >= grid.cols or h >= grid.rows:
                continue
                
            # Calcola origine casuale per inserire il recinto rettangolare
            r0 = rng.randint(0, grid.rows - h)
            c0 = rng.randint(0, grid.cols - w)
            
            # Costruisci i bordi fisici
            for r in range(r0, r0 + h):
                grid.set_obstacle(r, c0)
                grid.set_obstacle(r, c0 + w - 1)
            for c in range(c0, c0 + w):
                grid.set_obstacle(r0, c)
                grid.set_obstacle(r0 + h - 1, c)

    @classmethod
    def generate_bar(
        cls, 
        grid: Grid, 
        count: int, 
        thickness: int, 
        min_len: int, 
        max_len: int, 
        seed: Optional[int] = None
    ) -> None:
        """
        Genera segmenti H/V continui (barriere) di spessore prefissato, lasciando una singola cella aperta (varco).

        Args:
            grid: L'oggetto Griglia su cui operare.
            count: Numero di barriere da creare.
            thickness: Spessore in celle della barriera.
            min_len: Lunghezza minima della barriera.
            max_len: Lunghezza massima della barriera.
            seed: Seme casuale opzionale.
        """
        if count < 0 or thickness <= 0 or min_len <= 0 or max_len < min_len:
            raise ValueError("Parametri della barriera non validi.")

        rng = cls._get_rng(seed)
        
        for _ in range(count):
            orientation = rng.choice(["horizontal", "vertical"])
            length = rng.randint(min_len, max_len)
            
            if orientation == "horizontal":
                if thickness >= grid.rows or length >= grid.cols:
                    continue
                r0 = rng.randint(0, grid.rows - thickness)
                c0 = rng.randint(0, grid.cols - length)
                
                # Crea la barriera orizzontale
                for t in range(thickness):
                    for l in range(length):
                        grid.set_obstacle(r0 + t, c0 + l)
                        
                # Crea un varco (apertura traversabile)
                varco_c = rng.randint(c0, c0 + length - 1)
                for t in range(thickness):
                    grid.clear_cell(r0 + t, varco_c)
                    
            else:  # vertical
                if thickness >= grid.cols or length >= grid.rows:
                    continue
                r0 = rng.randint(0, grid.rows - length)
                c0 = rng.randint(0, grid.cols - thickness)
                
                # Crea la barriera verticale
                for l in range(length):
                    for t in range(thickness):
                        grid.set_obstacle(r0 + l, c0 + t)
                        
                # Crea un varco
                varco_r = rng.randint(r0, r0 + length - 1)
                for t in range(thickness):
                    grid.clear_cell(varco_r, c0 + t)

    @classmethod
    def generate_grid(
        cls, 
        rows: int, 
        cols: int, 
        types: List[str], 
        density: float = 0.2, 
        seed: Optional[int] = None
    ) -> Grid:
        """
        Inizializza e popola una nuova griglia unendo i tipi di ostacolo specificati.
        
        Tenta di approssimare con precisione la densità target finale specificata.

        Args:
            rows: Righe della griglia.
            cols: Colonne della griglia.
            types: Lista di stringhe con i tipi di ostacoli richiesti.
            density: Densità complessiva target (0.0..1.0).
            seed: Seme casuale globale.

        Returns:
            La griglia generata e pre-popolata.
        """
        grid = Grid(rows, cols)
        grid.types = list(types)
        if not types:
            return grid
            
        rng = cls._get_rng(seed)
        total_cells = rows * cols
        target_obstacles = int(total_cells * density)
        
        macro_types = [t for t in types if t != "simple"]
        
        # Generiamo prima gli ostacoli macrostrutturati (cluster, bar, recinti, ecc.)
        if macro_types:
            for t in macro_types:
                local_seed = rng.randint(0, 1000000)
                if t == "cluster":
                    num_c = max(1, int((target_obstacles * 0.3) / 10))
                    cls.generate_cluster(grid, num_c, 5, 15, seed=local_seed)
                elif t == "diagonal":
                    count = max(1, int((target_obstacles * 0.2) / 2.5))
                    cls.generate_diagonal(grid, count, seed=local_seed)
                elif t == "enclosure":
                    count = max(1, int((target_obstacles * 0.2) / 16))
                    cls.generate_enclosure(grid, count, 4, 8, seed=local_seed)
                elif t == "bar":
                    count = max(1, int((target_obstacles * 0.3) / 8))
                    cls.generate_bar(grid, count, thickness=1, min_len=5, max_len=12, seed=local_seed)

        # Se richiesto il tipo 'simple' o se la densità macro è inferiore al target
        current_density = np.sum(grid.state == 1) / total_cells
        if "simple" in types or current_density < density:
            remaining_density = max(0.01, density - current_density)
            local_seed = rng.randint(0, 1000000)
            cls.generate_simple(grid, remaining_density, seed=local_seed)
            
        logger.info(f"Generata griglia {rows}x{cols} con densità effettiva: {np.sum(grid.state == 1)/total_cells:.4f}")
        return grid
