### Contador de FPS para ser usado no render.py
import pygame
class UI:
    def __init__(self, screen, clock):
            """
            Inicializa os componentes da UI.
            """
            self.font = pygame.font.Font(None, 30)
            self.screen = screen
            self.clock = clock
            self.last_fps_text = ""
            self.fps_surface = None
            self.fps_font = pygame.font.Font(None, 30)
            print("P: UI inicializada.")

    def draw_fps(self):
        """
        Renderiza e desenha o contador de FPS na tela.
        """

        current_fps_text = f"FPS: {self.clock.get_fps():.0f}"
    
        if current_fps_text != self.last_fps_text:
            self.last_fps_text = current_fps_text
            self.fps_surface = self.fps_font.render(
                current_fps_text, True, (255, 255, 255)
            )
        
        if self.fps_surface: self.screen.blit(self.fps_surface, (10, 10))