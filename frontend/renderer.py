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

    #MELHORAR ISSO AQUI DEPOIS
    def _draw_dashed_rect(self, surface, color, rect, width=1, dash_length=10):
        """
        Desenha um retângulo tracejado.
        """
        x, y, w, h = rect
        
        for i in range(x, x + w, dash_length * 2):
            pygame.draw.line(surface, color, (i, y), (i + dash_length, y), width)
            pygame.draw.line(surface, color, (i, y + h), (i + dash_length, y + h), width)

        for i in range(y, y + h, dash_length * 2):
            pygame.draw.line(surface, color, (x, i), (x, i + dash_length), width)
            pygame.draw.line(surface, color, (x + w, i), (x + w, i + dash_length), width)

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
        
        #MELHORAR ISSO AQUI DEPOIS
        if globals.MARGIN_LINE:
            margin_color = (100, 100, 100)
            margin_rect = pygame.Rect(
                globals.MARGIN,
                globals.MARGIN,
                globals.SCREEN_WIDTH - 2 * globals.MARGIN,
                globals.SCREEN_HEIGHT - 2 * globals.MARGIN
            )

            self._draw_dashed_rect(self.screen, margin_color, margin_rect, width=2, dash_length=10)

        pygame.display.flip()

    def cleanup(self):
        """
        Finaliza o Pygame.
        """
        print("P: Finalizando renderer...")
        pygame.quit()