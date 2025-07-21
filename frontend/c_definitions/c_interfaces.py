import ctypes
import os
import sys
import globals
import state
from .c_structures import Boids, Grid, SpawnMode, BoundaryBehavior

def _configure_and_validate_path():
    """
    Configura e valida o caminho para a biblioteca C.
    """
    if globals.PLATFORM_SYSTEM not in globals.SUPPORTED_PLATFORMS:
        raise ValueError(f"P: Plataforma {globals.PLATFORM_SYSTEM} não suportada")

    extension = globals.LIBRARY_EXTENSIONS[globals.PLATFORM_SYSTEM]
    state.lib_path = os.path.join(".", "boids", f"libboids.{extension}")

    if not os.path.exists(state.lib_path):
        raise FileNotFoundError(f"P: Biblioteca não encontrada em {state.lib_path}")

def _set_function_signatures():
    """
    Define os tipos de argumento e retorno para as funções da lib C.
    """
    lib = state.boids_lib
    lib.initialize_boids.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    lib.initialize_boids.restype = ctypes.POINTER(Boids)

    lib.free_boids.argtypes = [ctypes.POINTER(Boids)]
    lib.free_boids.restype = None

    lib.create_grid.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_float]
    lib.create_grid.restype = ctypes.POINTER(Grid)

    lib.free_grid.argtypes = [ctypes.POINTER(Grid)]
    lib.free_grid.restype = None

    lib.update_boids.argtypes = [
        ctypes.POINTER(Boids),    # boids
        ctypes.POINTER(Grid),     # grid
        ctypes.c_int,             # behavior 
        ctypes.c_float,           # visual_range
        ctypes.c_float,           # protected_range
        ctypes.c_float,           # centering_factor
        ctypes.c_float,           # matching_factor
        ctypes.c_float,           # avoid_factor
        ctypes.c_float,           # turn_factor
        ctypes.c_float,           # bounce_factor
        ctypes.c_float,           # max_speed
        ctypes.c_float,           # min_speed
        ctypes.c_int,             # screen_width
        ctypes.c_int,             # screen_height
        ctypes.c_int,             # margin
        ctypes.c_int,             # mouse_x
        ctypes.c_int,             # mouse_y
        ctypes.c_bool,            # mouse_motion
        ctypes.c_bool,            # mouse_fear
        ctypes.c_bool,            # mouse_attraction
        ctypes.c_int,             # mouse_fear_radius
        ctypes.c_int,             # mouse_attraction_radius
    ]
    lib.update_boids.restype = None

    lib.initialize_seed.argtypes = []
    lib.initialize_seed.restype = None

def setup_library_interface():
    """
    Função principal para carregar e configurar a biblioteca C.
    """
    try:
        print("P: Configurando interface com a biblioteca C...")
        _configure_and_validate_path()
        state.boids_lib = ctypes.CDLL(state.lib_path)
        _set_function_signatures()
        state.library_loaded = True
        state.boids_lib.initialize_seed()
        print("P: Biblioteca carregada e configurada com sucesso!")
        return True
    except (ValueError, FileNotFoundError, AttributeError) as e:
        print(f"P: ERRO CRÍTICO ao configurar a biblioteca: {e}", file=sys.stderr)
        return False