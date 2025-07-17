import ctypes

boids_lib: ctypes.CDLL = None
lib_path: str = None
library_loaded: bool = False