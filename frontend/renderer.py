import pygame
import globals

class Renderer:
    def __init__(self):
        """
        Inicializa o Pygame e a janela de exibição.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((globals.SCREEN_WIDTH, globals.SCREEN_HEIGHT))
        pygame.display.set_caption("P: Simulação de Boids (C + Python)")
        print("P: Renderer inicializado.")

    def draw(self, simulation):
        """
        Desenha todos os boids na tela.
        """
        self.screen.fill(globals.BACKGROUND_COLOR)

        for i in range(globals.NUM_BIRDS):
            entity = simulation.boids1.contents.entities[i]
            pos = (int(entity.position.x), int(entity.position.y))
            pygame.draw.circle(self.screen, globals.BIRD_COLOR, pos, globals.BIRD_RADIUS, globals.BIRD_WIDTH)
        
        # for i in range(globals.NUM_BIRDS):
        #     entity = simulation.boids2.contents.entities[i]
        #     pos = (int(entity.position.x), int(entity.position.y))
        #     pygame.draw.circle(self.screen, globals.BIRD_COLOR_2, pos, globals.BIRD_RADIUS, globals.BIRD_WIDTH)

        pygame.display.flip()

    def cleanup(self):
        """
        Finaliza o Pygame.
        """
        print("P: Finalizando renderer...")
        pygame.quit()