import pygame
import globals
import math
#from UICOPY import UI
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
        self.model_triangle = [ 
            (self.bird_size * 0.75, 0), 
            (self.bird_size * -0.5, self.bird_size * -0.5), 
            (self.bird_size * -0.5, self.bird_size * 0.5)]
        
        self.UI = UI(self.screen, clock)

        pygame.display.set_caption("P: Simulação de Boids (C + Python)")
        print("P: Renderer inicializado.")

    def _get_color_by_speed(self, speed: float) -> tuple:
        """
        Calcula a cor de um boid com base na sua velocidade, usando um gradiente de 5 cores.
        """
        colors = [
            globals.VERY_SLOW_COLOR, 
            globals.SLOW_COLOR, 
            globals.MEDIUM_COLOR, 
            globals.FAST_COLOR, 
            globals.VERY_FAST_COLOR
        ]
        
        if globals.MAX_SPEED == globals.MIN_SPEED:
            return globals.VERY_SLOW_COLOR

        normalized_speed = (speed - globals.MIN_SPEED) / (globals.MAX_SPEED - globals.MIN_SPEED)
        normalized_speed = max(0.0, min(1.0, normalized_speed))
        segment_index = int(normalized_speed / 0.25)
        segment_index = min(segment_index, len(colors) - 2)
        segment_normalized_speed = (normalized_speed - segment_index * 0.25) / 0.25
        start_color = colors[segment_index]
        end_color = colors[segment_index + 1]
        r = start_color[0] + (end_color[0] - start_color[0]) * segment_normalized_speed
        g = start_color[1] + (end_color[1] - start_color[1]) * segment_normalized_speed
        b = start_color[2] + (end_color[2] - start_color[2]) * segment_normalized_speed
        
        return (int(r), int(g), int(b))
    
    def _get_triangle_points(self, entity):
        """
        Obtém os pontos do triângulo que representa o boid.
        """
        vx, vy = entity.velocity.vx, entity.velocity.vy
        
        if vx == 0 and vy == 0:
            cos_a = 1.0
            sin_a = 0.0
        else:
            magnitude = math.sqrt(vx * vx + vy * vy)
            cos_a = vx / magnitude
            sin_a = vy / magnitude

        rotated_points = []
        for mx, my in self.model_triangle:
            rx = (mx * cos_a) - (my * sin_a)
            ry = (mx * sin_a) + (my * cos_a)
            rotated_points.append((rx + entity.position.x, ry + entity.position.y))
        
        return rotated_points

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
        Desenha um boid na tela com cor baseada na velocidade.
        """
        vx, vy = entity.velocity.vx, entity.velocity.vy
        
        if globals.DYNAMIC_COLOR_ENABLED:
            speed = math.sqrt(vx*vx + vy*vy)
            color = self._get_color_by_speed(speed)
        else:
            speed = 0
            color = globals.STATIC_BOID_COLOR
        
        rotated_points = self._get_triangle_points(entity)

        pygame.draw.polygon(self.screen, color, rotated_points, 1)

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
        if not (globals.DRAW_PROTECTED_RANGE or globals.DRAW_VISUAL_RANGE): return

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
        if not globals.MARGIN_LINE: return
        
        margin_color = (100, 100, 100)
        margin_rect = pygame.Rect(
            globals.MARGIN,
            globals.MARGIN,
            globals.SCREEN_WIDTH - 2 * globals.MARGIN,
            globals.SCREEN_HEIGHT - 2 * globals.MARGIN
        )
        self._draw_dashed_rect(self.screen, margin_color, margin_rect, width, dash_length)

    def draw(self, simulation):
        """
        Desenha tela composta por boids, margens e UI.
        """
        entities = simulation.boids.contents.entities
        draw_boid_func = self.draw_boid

        self.draw_background()

        for i in range(globals.NUM_BIRDS):
            draw_boid_func(entities[i])
        
        self.draw_boids_range(simulation)
        self.draw_margins(globals.MARGIN_WIDTH, globals.MARGIN_DASH_LENGTH)

        self.UI.update()
        self.UI.draw()

        #RESPONSABILIDADE DA UI ESSE BOTAO
        # panel_edge_x = self.UI.panel_rect.x
        
        # current_surf = self.hide_panel_surf if globals.SHOW_UI_PANEL else self.show_panel_surf
        
        # self.toggle_button_rect = current_surf.get_rect(
        #     centery=globals.SCREEN_HEIGHT // 2,
        #     right=panel_edge_x - 5
        # )

        # self.screen.blit(current_surf, self.toggle_button_rect)

        pygame.display.flip()

    def cleanup(self):
        """
        Finaliza o Pygame.
        """
        print("P: Finalizando renderer...")
        pygame.quit()