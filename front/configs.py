import os
import globals

def configure_library_path():
    """
    Configura o caminho da biblioteca baseado no sistema operacional
    """
    if globals.platform_system not in globals.SUPPORTED_PLATFORMS:  
        raise ValueError(f"Plataforma {globals.platform_system} não suportada")
    
    extension = globals.LIBRARY_EXTENSIONS[globals.platform_system]
    globals.lib_path = os.path.join(".", "boids", f"libboids.{extension}")
    
    return globals.lib_path

def validate_library_path():
    """
    Valida se o caminho da biblioteca existe
    """
    if not globals.lib_path:
        raise ValueError("Caminho da biblioteca não configurado")
    
    if not os.path.exists(globals.lib_path):
        error_msg = f"Biblioteca não encontrada em {globals.lib_path}"
        debug_info = f"\nDiretório atual: {globals.current_dir}"
        
        try:
            parent_files = os.listdir('..')
            debug_info += f"\nArquivos no diretório pai: {parent_files}"
        except OSError:
            debug_info += "\nNão foi possível listar arquivos do diretório pai"
        
        raise FileNotFoundError(error_msg + debug_info)
    
    return True

# def get_library_info():
#     """
#     Retorna informações sobre a biblioteca
#     """
#     return {
#         "platform": globals.platform_system,
#         "path": globals.lib_path,
#         "exists": os.path.exists(globals.lib_path) if globals.lib_path else False,
#         "current_dir": globals.current_dir,
#         "loaded": globals.library_loaded
#     }