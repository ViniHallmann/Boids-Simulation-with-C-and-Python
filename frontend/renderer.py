import pygame
import globals
import math
class Renderer:
    def __init__(self):
        """
        Inicializa o Pygame e a janela de exibição.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((globals.SCREEN_WIDTH, globals.SCREEN_HEIGHT))
        self.blur_surface = pygame.Surface((globals.SCREEN_WIDTH, globals.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.blur_surface.fill((0, 0, 0, globals.BLUR_TRANSPARENCY_VALUE))
        # self.background_image = pygame.image.load("images/space.jpg").convert()
        # self.background_image = pygame.transform.scale(
        #     self.background_image, (globals.SCREEN_WIDTH, globals.SCREEN_HEIGHT)
        # )

        self.boid_size = 6
        self.model_triangle = [
            (self.boid_size * 0.75, 0),                           # Ponta da frente
            (self.boid_size * -0.5, self.boid_size * -0.5),       # Ponto de trás (inferior)
            (self.boid_size * -0.5, self.boid_size * 0.5)         # Ponto de trás (superior)
        ]
        pygame.display.set_caption("P: Simulação de Boids (C + Python)")
        print("P: Renderer inicializado.")

    def _draw_dashed_rect(self, surface, color, rect, width=1, dash_length=10):
        """
        Molde de retângulo tracejado.
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

        #self.screen.blit(self.background_image, (0, 0))

        if globals.BLUR:
            self.screen.blit(self.blur_surface, (0, 0))
        else:
            self.screen.fill(globals.BACKGROUND_COLOR)

        for i in range(globals.NUM_BIRDS):
            entity = simulation.boids1.contents.entities[i]
            angle = math.atan2(entity.velocity.vy, entity.velocity.vx)
            rotated_points = []
            for mx, my in self.model_triangle:
                
                rx = (mx * math.cos(angle)) - (my * math.sin(angle))
                ry = (mx * math.sin(angle)) + (my * math.cos(angle))

                screen_x = rx + entity.position.x
                screen_y = ry + entity.position.y

                rotated_points.append((screen_x, screen_y))

            pygame.draw.polygon(self.screen, globals.BIRD_COLOR, rotated_points, 1)

            # Desenho do círculo ao redor do boid
            # pos = (int(entity.position.x), int(entity.position.y))
            # pygame.draw.circle(self.screen, globals.BIRD_COLOR, pos, globals.BIRD_RADIUS, globals.BIRD_WIDTH)


        if globals.MARGIN_LINE:
            margin_color = (100, 100, 100)
            margin_rect = pygame.Rect(
                globals.MARGIN,
                globals.MARGIN,
                globals.SCREEN_WIDTH - 2 * globals.MARGIN,
                globals.SCREEN_HEIGHT - 2 * globals.MARGIN
            )

            #pygame.draw.rect(self.screen, margin_color, margin_rect, 2)
            self._draw_dashed_rect(self.screen, margin_color, margin_rect, width=2, dash_length=10)

        pygame.display.flip()

    def cleanup(self):
        """
        Finaliza o Pygame.
        """
        print("P: Finalizando renderer...")
        pygame.quit()