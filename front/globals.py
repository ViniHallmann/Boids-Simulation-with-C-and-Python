import platform
import os

boids_lib = None
lib_path = None
platform_system = platform.system()
current_dir = os.getcwd()

SUPPORTED_PLATFORMS = ["Windows", "Darwin", "Linux"]
LIBRARY_EXTENSIONS = {
    "Windows": "dll",
    "Darwin": "dylib",
    "Linux": "so"
}

library_loaded = False