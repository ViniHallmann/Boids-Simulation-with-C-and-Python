import ctypes
import os
import sys
import globals
import state
from .c_structures import Boids, Grid

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
    lib.initialize_boids.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int] # num_boids, screen_width, screen_height, spawn_mode
    lib.initialize_boids.restype = ctypes.POINTER(Boids) # Boids

    lib.free_boids.argtypes = [ctypes.POINTER(Boids)] # Boids
    lib.free_boids.restype = None

    lib.create_grid.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_float] # screen_width, screen_height, cell_size
    lib.create_grid.restype = ctypes.POINTER(Grid) # Grid

    lib.free_grid.argtypes = [ctypes.POINTER(Grid)] # Grid
    lib.free_grid.restype = None

    lib.update_boids.argtypes = [
        ctypes.POINTER(Boids), ctypes.POINTER(Grid),
        ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float, # visual_range, protected_range, centering_factor, matching_factor, avoid_factor
        ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float, # turn_factor, max_speed, min_speed
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, # screen_width, screen_height, margin
        ctypes.c_bool, ctypes.c_bool, ctypes.c_bool, # mouse_motion, mouse_fear, mouse_attraction
        ctypes.c_int, ctypes.c_int # mouse_fear_radius, mouse_attraction_radius
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