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
            print("P: UI inicializada.")

    def draw_fps(self):
        """
        Renderiza e desenha o contador de FPS na tela.
        """

        fps_text = f"FPS: {self.clock.get_fps():.0f}"
        fps_surface = self.font.render(fps_text, True, pygame.Color("white"))
        self.screen.blit(fps_surface, (10, 10))