import sys
from c_definitions import c_interfaces
from app import App

def main():
    """
    Ponto de entrada principal da aplicação.
    """
    if not c_interfaces.setup_library_interface(): sys.exit(1)

    app = App()
    app.run()

    print("P: Aplicação encerrada.")
    sys.exit(0)

if __name__ == "__main__":
    main()