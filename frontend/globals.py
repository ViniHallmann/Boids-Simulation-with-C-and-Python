import platform
from c_definitions.c_structures import SpawnMode
from c_definitions.c_structures import BoundaryBehavior

# --- DEFAULT SETTINGS ---
DEFAULT_SETTINGS = {
    "TURN_FACTOR": 0.2,
    "VISUAL_RANGE": 45.0,
    "PROTECTED_RANGE": 6.0,
    "CENTERING_FACTOR": 0.0005,
    "AVOID_FACTOR": 0.1,
    "MATCHING_FACTOR": 0.05,
    "MIN_SPEED": 3.0,
    "MAX_SPEED": 6.0,
    "BOUNCE_FACTOR": 0.1,
    "BOUNDARY_BEHAVIOR": BoundaryBehavior.BOUNDARY_TURN,
    "NUM_BIRDS": 1500,
    "MARGIN_LINE": True,
    "DRAW_PROTECTED_RANGE": False,
    "DRAW_VISUAL_RANGE": False,
}

# --- NON-CRITICAL VARIABLES ---
TURN_FACTOR:        float = DEFAULT_SETTINGS["TURN_FACTOR"]
VISUAL_RANGE:       float = DEFAULT_SETTINGS["VISUAL_RANGE"]
PROTECTED_RANGE:    float = DEFAULT_SETTINGS["PROTECTED_RANGE"]
CENTERING_FACTOR:   float = DEFAULT_SETTINGS["CENTERING_FACTOR"]
AVOID_FACTOR:       float = DEFAULT_SETTINGS["AVOID_FACTOR"]
MATCHING_FACTOR:    float = DEFAULT_SETTINGS["MATCHING_FACTOR"]
BOUNCE_FACTOR:      float = DEFAULT_SETTINGS["BOUNCE_FACTOR"]
BOUNDARY_BEHAVIOR:  BoundaryBehavior = DEFAULT_SETTINGS["BOUNDARY_BEHAVIOR"]
MAX_SPEED:          float = DEFAULT_SETTINGS["MAX_SPEED"]
MIN_SPEED:          float = DEFAULT_SETTINGS["MIN_SPEED"]

MARGIN_WIDTH:       int = 2
MARGIN_DASH_LENGTH: int = 10
MARGIN:             int = 150
MARGIN_LINE:        bool = DEFAULT_SETTINGS["MARGIN_LINE"]

DRAW_PROTECTED_RANGE: bool = DEFAULT_SETTINGS["DRAW_PROTECTED_RANGE"]
DRAW_VISUAL_RANGE:    bool = DEFAULT_SETTINGS["DRAW_VISUAL_RANGE"]

SHOW_UI_PANEL = True
PAUSED: bool = False

BIRD_SIZE: int = 3
BIRD_WIDTH:         int   = 1
BIRD_RADIUS:        float = 2.5
BIRD_COLOR:         tuple = (255, 255, 255)

BACKGROUND_COLOR:   tuple = (10, 20, 40)
FPS: int = 60
BLUR: bool = False
BLUR_TRANSPARENCY_VALUE: int = 15

MOUSE_POS:          tuple = (0, 0)

#ADICIONAR BOTAO DISSO AQUI
MOUSE_MOTION:       bool = False
MOUSE_FEAR:         bool = False
MOUSE_ATTRACTION:   bool = False
MOUSE_FEAR_RADIUS:          int = 100
MOUSE_ATTRACTION_RADIUS:    int = 200
#####

# --- CRITICAL VARIABLES ---
SCREEN_WIDTH:           int = 1300
SCREEN_HEIGHT:          int = 700
NUM_BIRDS:              int = DEFAULT_SETTINGS["NUM_BIRDS"]
UI_PANEL_RECT = None # Usado pela UI e Simulação

# Platform-specific configurations
PLATFORM_SYSTEM: str = platform.system()
SUPPORTED_PLATFORMS = ["Windows", "Darwin", "Linux"]
LIBRARY_EXTENSIONS = {
    "Windows": "dll",
    "Darwin": "so",
    "Linux": "so"
}