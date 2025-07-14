import ctypes
import sys
import globals
import configs

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

def call_c_function():
    """
    Chama a função da biblioteca C
    """
    if not globals.library_loaded:  return False
    
    try:
        globals.boids_lib.print_message()
        return True
        
    except Exception as e:
        print(f"Erro ao chamar função da biblioteca: {e}")
        return False

def main():
    """
    Função principal
    """
    if not load_library(): sys.exit(1)

    call_c_function()



if __name__ == "__main__":
    main()