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

        self.simulation     = Simulation(globals.NUM_BIRDS)
        self.clock          = pygame.time.Clock()
        self.renderer       = Renderer(self.clock)
        self.input_handler  = InputHandler(self)
        self.running        = True

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

    def restart_simulation(self, num_boids=None):
        """
        Responsabilidade ÚNICA: Limpa a simulação antiga e cria uma nova.
        Se num_boids não for especificado, usa o valor atual de globals.
        """
        if num_boids is not None:
            globals.NUM_BIRDS = num_boids
        print(f"P: Reiniciando simulação com {globals.NUM_BIRDS} boids...")
        
        self.simulation.cleanup()
        self.simulation = Simulation(globals.NUM_BIRDS)