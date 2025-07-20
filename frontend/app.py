import pygame
import globals
from simulation     import Simulation
from renderer       import Renderer
from input_handler  import InputHandler

class App:
    def __init__(self):
        """
        Inicializa os componentes principais da aplicação.
        """
        self.simulation = Simulation()
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.clock)
        self.input_handler = InputHandler(self)
        self._setup_event_handlers()
        self.running = True
            
    def run(self):
        """
        Executa o loop principal da aplicação.
        """
        while self.running:
            self.input_handler.process_events()
            self.simulation.update()
            self.renderer.draw(self.simulation)
            self.clock.tick(globals.FPS)
        
        self.cleanup()

    def cleanup(self):
        """
        Chama a limpeza de todos os componentes.
        """
        self.simulation.cleanup()
        self.renderer.cleanup()