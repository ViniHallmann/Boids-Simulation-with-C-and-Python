import pygame
import globals
import math
from UI import UI
class Renderer:
    def __init__(self, clock):
        """
        Inicializa o Pygame e a janela de exibição.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((globals.SCREEN_WIDTH, globals.SCREEN_HEIGHT))
        self.blur_surface = pygame.Surface((globals.SCREEN_WIDTH, globals.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.blur_surface.fill((0, 0, 0, globals.BLUR_TRANSPARENCY_VALUE))
        self.bird_size = globals.BIRD_SIZE
        self.model_triangle = [ (self.bird_size * 0.75, 0), (self.bird_size * -0.5, self.bird_size * -0.5), (self.bird_size * -0.5, self.bird_size * 0.5)]
        self.UI = UI(self.screen, clock)
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

    def draw_boid(self, entity):
        """
        Desenha um boid na tela.
        """
        vx, vy = entity.velocity.vx, entity.velocity.vy
        speed = math.sqrt(vx*vx + vy*vy)

        if speed == 0:
            cos_a = 1.0
            sin_a = 0.0
        else:
            cos_a = vx / speed
            sin_a = vy / speed

        rotated_points = []
        for mx, my in self.model_triangle:
            rx = (mx * cos_a) - (my * sin_a)
            ry = (mx * sin_a) + (my * cos_a)

            screen_x = rx + entity.position.x
            screen_y = ry + entity.position.y

            rotated_points.append((screen_x, screen_y))

        pygame.draw.polygon(self.screen, globals.BIRD_COLOR, rotated_points, 1)
    
    def draw_background(self):
        """
        Desenha o fundo da tela.
        """
        if globals.BLUR:
            self.screen.blit(self.blur_surface, (0, 0))
        else:
            self.screen.fill(globals.BACKGROUND_COLOR)
        
    def draw_boids_range(self, simulation):
        """
        Desenha os raios de proteção e visualização dos boids.
        """
        if globals.DRAW_PROTECTED_RANGE or globals.DRAW_VISUAL_RANGE:
            for i in range(globals.NUM_BIRDS):
                entity = simulation.boids.contents.entities[i]
                pos = (int(entity.position.x), int(entity.position.y))

                if globals.DRAW_PROTECTED_RANGE:
                    pygame.draw.circle(self.screen, (255, 0, 0), pos, int(globals.PROTECTED_RANGE), 1)
                
                if globals.DRAW_VISUAL_RANGE:
                    pygame.draw.circle(self.screen, (0, 255, 0), pos, int(globals.VISUAL_RANGE), 1)
    
    def draw_margins(self, width=2, dash_length=10):
        """
        Desenha as margens da tela.
        """
        margin_color = (100, 100, 100)
        margin_rect = pygame.Rect(
            globals.MARGIN,
            globals.MARGIN,
            globals.SCREEN_WIDTH - 2 * globals.MARGIN,
            globals.SCREEN_HEIGHT - 2 * globals.MARGIN
        )
        # DESENHO DA MARGEM RETA
            #pygame.draw.rect(self.screen, margin_color, margin_rect, 2)
        self._draw_dashed_rect(self.screen, margin_color, margin_rect, width, dash_length)

    def draw(self, simulation):
        """
        Desenha tela composta por boids, margens e UI.
        """

        self.draw_background()

        for i in range(globals.NUM_BIRDS):
            entity = simulation.boids.contents.entities[i]
            self.draw_boid(entity)
        
        self.draw_boids_range(simulation)
            
        if globals.MARGIN_LINE:
            self.draw_margins(globals.MARGIN_WIDTH, globals.MARGIN_DASH_LENGTH)

        self.UI.draw()

        pygame.display.flip()

    def cleanup(self):
        """
        Finaliza o Pygame.
        """
        print("P: Finalizando renderer...")
        pygame.quit()