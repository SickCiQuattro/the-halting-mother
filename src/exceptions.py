class PathfindingError(Exception):
    """Classe base per tutte le eccezioni del sistema di pathfinding."""
    pass

class InvalidCoordinateError(PathfindingError):
    """Eccezione sollevata quando le coordinate fornite sono al di fuori della griglia."""
    pass

class PathReconstructionError(PathfindingError):
    """Eccezione sollevata in caso di fallimento nella ricostruzione del cammino dai landmark."""
    pass
