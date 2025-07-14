import platform
import os

boids_lib:       str = None
lib_path:        str = None
platform_system: str = platform.system()
current_dir:     str = os.getcwd()

VISUAL_RANGE:     float = 75.0
PROTECTED_RANGE:  float = 8.0
CENTERING_FACTOR: float = 0.0005
MATCHING_FACTOR:  float = 0.05
AVOID_FACTOR:     float = 0.05
TURN_FACTOR:      float = 0.2
MAX_SPEED:        float = 6.0
MIN_SPEED:        float = 3.0

SCREEN_WIDTH:           int  = 1200
SCREEN_HEIGHT:          int = 800
SCREEN_WIDTH_MARGIN:    int  = 200
SCREEN_HEIGHT_MARGIN:   int = 100
MARGIN:                 int = 175

NUM_BIRDS:      int     = 1000
BIRD_WIDTH:     int     = 1
BIRD_RADIUS:    float   = 2.5

BIRD_COLOR:         tuple = (255, 255, 255)
BACKGROUND_COLOR:   tuple = (10, 20, 40)


SUPPORTED_PLATFORMS = ["Windows", "Darwin", "Linux"]
LIBRARY_EXTENSIONS = {
    "Windows": "dll",
    "Darwin": "so",
    "Linux": "so"
}

library_loaded: bool = False