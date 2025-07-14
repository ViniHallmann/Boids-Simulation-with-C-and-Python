import ctypes
import sys
import globals
import configs

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
##################################################################################

def set_functions_args():
    """
    Configura os tipos de argumentos e retorno das funções da biblioteca C
    """
    if not globals.library_loaded:
        print("Biblioteca não carregada.")
        return False
    
    try:
        globals.boids_lib.initialize_boids.argtypes = [ctypes.c_int]
        globals.boids_lib.initialize_boids.restype = ctypes.POINTER(Boids)

        globals.boids_lib.update_boids.argtypes = [ctypes.POINTER(Boids)]
        globals.boids_lib.update_boids.restype = None

        globals.boids_lib.free_boids.argtypes = [ctypes.POINTER(Boids)]
        globals.boids_lib.free_boids.restype = None
        
        return True
        
    except Exception as e:
        print(f"Erro ao configurar funções: {e}")
        return False

def main():
    """
    Função principal
    """
    if not load_library() or not set_functions_args(): sys.exit(1)

    boids = globals.boids_lib.initialize_boids(globals.NUM_BIRDS)
    if not boids: sys.exit(1)

    boid_zero = boids.contents.entities[0]
    print(f"Python: Posição inicial do Boid 0: ({boid_zero.position.x:.2f}, {boid_zero.position.y:.2f})")

    print("\nPython: Chamando a atualização do C...")
    globals.boids_lib.update_boids(boids)
    globals.boids_lib.update_boids(boids)
    
    print(f"Python: Nova posição do Boid 0: ({boid_zero.position.x:.2f}, {boid_zero.position.y:.2f})\n")

    print("Python: Pedindo para C liberar a memória...")
    globals.boids_lib.free_boids(boids)
    print("Python: Fim do programa.")


if __name__ == "__main__":
    main()