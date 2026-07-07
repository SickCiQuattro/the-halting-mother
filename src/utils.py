from src.grid import Grid, Coordinate
from src.exceptions import InvalidCoordinateError

def parse_coords(coords_str: str) -> Coordinate:
    """
    Parsa una stringa contenente coordinate nel formato 'row,col' o '(row,col)'.

    Args:
        coords_str: Stringa in ingresso da analizzare.

    Returns:
        La coordinata parsa come tupla di due interi.

    Raises:
        InvalidCoordinateError: Se il formato della stringa non è corretto o contiene caratteri non numerici.
    """
    cleaned = coords_str.replace('(', '').replace(')', '').strip()
    parts = cleaned.split(',')
    if len(parts) != 2:
        raise InvalidCoordinateError(f"Formato coordinate non valido: '{coords_str}'. Deve essere nel formato 'riga,colonna'")
    try:
        row = int(parts[0].strip())
        col = int(parts[1].strip())
        return row, col
    except ValueError as e:
        raise InvalidCoordinateError(f"Le coordinate devono essere valori interi validi: '{coords_str}'") from e

def format_landmarks(landmarks: list[tuple[Coordinate, int]]) -> str:
    """
    Formatta la sequenza ordinata di landmark in una stringa altamente leggibile.

    Args:
        landmarks: Lista di tuple (coordinata, tipo_cammino) prodotte dall'algoritmo di pathfinding.

    Returns:
        Una stringa formattata multilinea descrittiva dei passaggi.
    """
    if not landmarks:
        return "Nessun cammino minimo individuato o sequenza landmark vuota."
    
    parts: list[str] = []
    for idx, (coord, tipo) in enumerate(landmarks):
        if idx == 0:
            parts.append(f"Sorgente {coord}")
        else:
            tipo_str = "Tipo 1 (diagonale prima, cardinale dopo)" if tipo == 1 else "Tipo 2 (cardinale prima, diagonale dopo)"
            parts.append(f"  -> {coord} tramite {tipo_str}")
            
    return "\n".join(parts)

def print_grid_visual(
    grid: Grid,
    origin: Coordinate | None = None,
    dest: Coordinate | None = None,
    path: list[Coordinate] | None = None
) -> None:
    """
    Stampa a terminale una griglia visuale ASCII stilizzata.

    Utile per il debug visivo immediato di piccoli test in fase di sviluppo.

    Args:
        grid: L'oggetto Griglia da stampare.
        origin: Coordinata dell'origine (opzionale).
        dest: Coordinata della destinazione (opzionale).
        path: Lista di coordinate del cammino completo ricostruito (opzionale).
    """
    path_cells = set(path) if path else set()

    for r in range(grid.rows):
        row_chars: list[str] = []
        for c in range(grid.cols):
            cell: Coordinate = (r, c)
            if cell == origin:
                row_chars.append("O")
            elif cell == dest:
                row_chars.append("D")
            elif cell in path_cells:
                row_chars.append("*")  # Cella del cammino ottimale ricostruito
            else:
                row_chars.append(Grid.carattere_ascii(grid.state[r, c]))
        print(" ".join(row_chars))
