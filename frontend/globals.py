import platform
from c_definitions.c_structures import SpawnMode
from c_definitions.c_structures import BoundaryBehavior

# VARIAVEIS NAO CRITICAS - Podem ser alteradas em tempo de execucao sem reiniciar o programa.
# Implementar uma interface para alterar essas variaveis em tempo de execucao.
TURN_FACTOR:        float = 0.2
VISUAL_RANGE:       float = 45.0
PROTECTED_RANGE:    float = 6.0

# COESAO
CENTERING_FACTOR:   float = 0.0005

# SEPARACAO
AVOID_FACTOR:       float = 0.1

# ALINHAMENTO
MATCHING_FACTOR:    float = 0.05

# BOUNCE_FACTOR:     float = 0.1
BOUNCE_FACTOR:      float = 0.1
BOUNDARY_BEHAVIOR: BoundaryBehavior = BoundaryBehavior.BOUNDARY_TURN
  
MAX_SPEED:          float = 6.0
MIN_SPEED:          float = 3.0

MARGIN_WIDTH:       int = 2
MARGIN_DASH_LENGTH: int = 10
MARGIN:             int   = 150
MARGIN_LINE:        bool  = True

DRAW_PROTECTED_RANGE:   bool = False
DRAW_VISUAL_RANGE:      bool = False

SHOW_UI_PANEL = True

BIRD_SIZE: int = 3
# WHEN BIRD IS DRAWN AS A CIRCLE
BIRD_WIDTH:         int   = 1
BIRD_RADIUS:        float = 2.5
################################
BIRD_COLOR:         tuple = (255, 255, 255)

BACKGROUND_COLOR:   tuple = (10, 20, 40)
FPS: int = 60
BLUR: bool = False
BLUR_TRANSPARENCY_VALUE: int = 15

MOUSE_POS:          tuple = (0, 0)
MOUSE_MOTION:       bool = True
MOUSE_FEAR:         bool = False
MOUSE_ATTRACTION:   bool = False
MOUSE_FEAR_RADIUS:          int = 100
MOUSE_ATTRACTION_RADIUS:    int = 100

PAUSED:                         bool = False

# QUAL A DIFERENCA ENTRE RESTART E RESTART COM BOIDS? 
# o que significa resetar com boids?
RESTART_SIMULATION:             bool = False 
# RESTART_SIMULATION_WITH_BOIDS:  bool = False


# VARIAVEIS CRITICAS - So podem ser alteradas em tempo de execucao caso o "run" do programa seja reiniciado. 
# Pra rodar em tempo de execucao vai precisar dar um cleanup e instanciar nova simulation()
SCREEN_WIDTH:           int = 1300
SCREEN_HEIGHT:          int = 700
SCREEN_WIDTH_MARGIN:    int = 200
SCREEN_HEIGHT_MARGIN:   int = 100
NUM_BIRDS:              int = 1000
PLATFORM_SYSTEM: str = platform.system()
SUPPORTED_PLATFORMS = ["Windows", "Darwin", "Linux"]
LIBRARY_EXTENSIONS = {
    "Windows": "dll",
    "Darwin": "so",
    "Linux": "so"
}
