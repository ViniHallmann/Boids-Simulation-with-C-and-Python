import pygame
import globals
from simulation import Simulation
from renderer import Renderer

class App:
    def __init__(self):
        """
        Inicializa os componentes principais da aplicação.
        """
        self.simulation = Simulation()
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.clock)
        
        self.running = True

    def _handle_events(self):
        """
        Trata os eventos de entrada.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                self.running = False
            elif event.type == pygame.MOUSEMOTION:
                globals.MOUSE_POS = pygame.mouse.get_pos()
            
    def run(self):
        """
        Executa o loop principal da aplicação.
        """
        while self.running:
            self._handle_events()
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