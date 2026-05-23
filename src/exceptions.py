class PathfindingError(Exception):
    """Classe base per tutte le eccezioni del sistema di pathfinding."""
    pass

class GridError(PathfindingError):
    """Eccezione sollevata per errori relativi alla griglia."""
    pass

class InvalidCoordinateError(GridError):
    """Eccezione sollevata quando le coordinate fornite sono al di fuori della griglia."""
    pass

class CoordinateBlockedError(GridError):
    """Eccezione sollevata quando si tenta di posizionare un ostacolo o sorgente su una cella non valida."""
    pass

class PathReconstructionError(PathfindingError):
    """Eccezione sollevata in caso di fallimento nella ricostruzione del cammino dai landmark."""
    pass
