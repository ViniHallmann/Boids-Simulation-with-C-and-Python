import ctypes
import sys
import globals
import configs
import pygame

# CLASSES PARA REPRESENTAR ESTRUTURAS C
# JA DA PRA QUEBRAR ISSO AQUI EM OUTROS CODIGO, EU SO PRECISO TER AS ESTRUTURAS REPRESENTADAS, TALVEZ DEIXAR ISSO EM GLOBALS?
class Position(ctypes.Structure):
    """
    Classe para representar a posição de um boid
    """
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
    ]
    
class Velocity(ctypes.Structure):
    """
    Classe para representar a velocidade de um boid
    """
    _fields_ = [
        ("vx", ctypes.c_float),
        ("vy", ctypes.c_float),
    ]

class Entity(ctypes.Structure):
    """
    Classe para representar um boid
    """
    _fields_ = [
        ("position", Position),
        ("velocity", Velocity),
    ]

class Boids(ctypes.Structure):
    """
    Classe para representar o conjunto de boids
    """
    pass

#TEM QUE FAZER DESSE JEITO POIS BOIDS NAO RECONHECE O Entity ANTES DE SER DEFINIDO
Boids._fields_ = [
    ("entities", ctypes.POINTER(Entity)),
    ("count", ctypes.c_int),
]
##################################################################################

# CHAMADAS A FUNÇÕES DA BIBLIOTECA C
# MINHA IDEIA EH FAZER COM QUE TODAS CHAMADAS SEJAM FEITAS AQUI PARA FILTRAR O QUE ESTA SENDO CHAMADO 
# E SE ESTA SENDO PASSADO CORRETAMENTE OS PARAMETROS
def call_c(nomefuncao: str = "print_message"):
    """
    Chama a função da biblioteca C
    """
    if not globals.library_loaded:  return False
    
    try:
        globals.boids_lib.__getattr__(nomefuncao)()  
        return True
        
    except Exception as e:
        print(f"Erro ao chamar função da biblioteca: {e}")
        return False
##################################################################################

# UTIL
# CRIAR utils.py PARA FUNCOES UTILITARIAS
def load_library():
    """
    Carrega a biblioteca C
    """
    try:
        configs.configure_library_path()
        configs.validate_library_path()
        
        globals.boids_lib = ctypes.CDLL(globals.lib_path)
        globals.library_loaded = True
        
        return True
        
    except Exception as e:
        print(f"Erro ao carregar biblioteca: {e}")
        return False

def set_functions_args():
    """
    Configura os tipos de argumentos e retorno das funções da biblioteca C
    """
    if not globals.library_loaded:
        print("Biblioteca não carregada.")
        return False
    
    try:
        globals.boids_lib.initialize_boids.argtypes = [ctypes.c_int]        # count
        globals.boids_lib.initialize_boids.restype = ctypes.POINTER(Boids)  # ponteiro para Boids

        globals.boids_lib.update_boids.argtypes = [ctypes.POINTER(Boids)]   # count
        globals.boids_lib.update_boids.restype = None

        globals.boids_lib.free_boids.argtypes = [ctypes.POINTER(Boids)] # ponteiro para Boids
        globals.boids_lib.free_boids.restype = None

        globals.boids_lib.update_boids.argtypes = [
            ctypes.POINTER(Boids),  # boids
            ctypes.c_float,         # visual_range
            ctypes.c_float,         # protected_range
            ctypes.c_float,         # centering_factor
            ctypes.c_float,         # matching_factor
            ctypes.c_float,         # avoid_factor
            ctypes.c_float,         # turn_factor
            ctypes.c_float,         # max_speed
            ctypes.c_float,         # min_speed
            ctypes.c_int,           # screen_width
            ctypes.c_int,           # screen_height
            ctypes.c_int            # margin
        ]
        globals.boids_lib.update_boids.restype = None
        
        return True
        
    except Exception as e:
        print(f"Erro ao configurar funções: {e}")
        return False
##################################################################################
def setup():
    """
    Configura o ambiente, carrega a biblioteca e define os tipos de funções.
    """
    if not load_library():
        print("Erro ao carregar a biblioteca.")
        sys.exit(1)
    
    if not set_functions_args():
        print("Erro ao configurar as funções da biblioteca.")
        sys.exit(1)

def initialize_pygame():
    """
    Inicializa o Pygame e configura a tela.
    """
    pygame.init()
    screen = pygame.display.set_mode((globals.SCREEN_WIDTH, globals.SCREEN_HEIGHT))
    pygame.display.set_caption("Simulação de Boids (C + Python)")
    clock = pygame.time.Clock()
    return screen, clock

def _handle_events():
    """
    Trata os eventos do Pygame.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                return False
    return True

def main():
    """
    Função principal que carrega a biblioteca, inicializa o Pygame e executa o loop de simulação/desenho.
    """
    setup()
    screen, clock = initialize_pygame()
    boids = globals.boids_lib.initialize_boids(globals.NUM_BIRDS)

    running = True
    while running:
        running = _handle_events()
        globals.boids_lib.update_boids(boids, globals.VISUAL_RANGE, globals.PROTECTED_RANGE, globals.CENTERING_FACTOR, globals.MATCHING_FACTOR, globals.AVOID_FACTOR, globals.TURN_FACTOR, globals.MAX_SPEED, globals.MIN_SPEED, globals.SCREEN_WIDTH, globals.SCREEN_HEIGHT, globals.MARGIN)

        screen.fill(globals.BACKGROUND_COLOR)

        for i in range(globals.NUM_BIRDS):
            boid_entity = boids.contents.entities[i]
            pos_x = int(boid_entity.position.x)
            pos_y = int(boid_entity.position.y)
            
            pygame.draw.circle(screen, globals.BIRD_COLOR, (pos_x, pos_y), globals.BIRD_RADIUS, globals.BIRD_WIDTH)

        pygame.display.flip()
        clock.tick(30)

    print("Finalizando... Liberando memória.")
    globals.boids_lib.free_boids(boids)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()