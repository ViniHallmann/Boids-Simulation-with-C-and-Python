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
        self.running = True
            
    def run(self):
        """
        Executa o loop principal da aplicação.
        """
        while self.running:
            self.input_handler.process_events()
            
            # Check for restart requests
            if globals.RESTART_SIMULATION:
                self.restart_simulation()
                globals.RESTART_SIMULATION = False
            elif globals.RESTART_SIMULATION_WITH_BOIDS is not None:
                self.restart_simulation(globals.RESTART_SIMULATION_WITH_BOIDS)
                globals.RESTART_SIMULATION_WITH_BOIDS = None
            
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

    def restart_simulation(self, new_num_birds=None):
        """
        Reinicia a simulação com um novo número de boids, se especificado.
        """
        if new_num_birds is not None:
            globals.NUM_BIRDS = new_num_birds
            print(f"P: Reiniciando simulação com {new_num_birds} boids...")
        else:
            print("P: Reiniciando simulação...")
        
        # Limpa a simulação atual
        self.simulation.cleanup()
        
        # Cria uma nova simulação
        self.simulation = Simulation()