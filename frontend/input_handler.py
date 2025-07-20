import pygame
import globals

class InputHandler:
    def __init__(self, app):
        """
        Inicializa o manipulador de eventos.
        Recebe a instância da App para poder alterar seu estado (ex: self.app.running).
        """
        self.app = app
        self._setup_event_handlers()

    def process_events(self):
        """
        Processa a fila de eventos do Pygame usando o dispatcher.
        Este método será chamado a cada quadro pelo loop principal da App.
        """
        for event in pygame.event.get():
            handler = self.event_handlers.get(event.type)
            if handler:
                handler(event)

    def _setup_event_handlers(self):
        """
        Configura o dicionário que mapeia eventos para funções de tratamento.
        """
        self.event_handlers = {
            pygame.QUIT: self._quit,
            pygame.KEYDOWN: self._key_down,
            pygame.MOUSEMOTION: self._mouse_motion,
            pygame.MOUSEBUTTONDOWN: self._mouse_button_down,
        }
    
    def _quit(self, event):
        """
        Manipulador para o evento de saída.
        """
        self.app.running = False
    
    def _key_down(self, event):
        """
        Manipulador para teclas pressionadas.
        """
        if event.key == pygame.K_q:
            self.app.running = False
        elif event.key == pygame.K_b:
            globals.BLUR = not globals.BLUR
            print(f"P: Blur {'ativado' if globals.BLUR else 'desativado'}.")
        elif event.key == pygame.K_m:
            globals.MOUSE_MOTION = not globals.MOUSE_MOTION
            print(f"P: MOUSE_MOTION {'ativado' if globals.MOUSE_MOTION else 'desativado'}.")
        elif event.key == pygame.K_p: 
            globals.DRAW_PROTECTED_RANGE = not globals.DRAW_PROTECTED_RANGE
            print(f"P: Desenho do raio de proteção {'ativado' if globals.DRAW_PROTECTED_RANGE else 'desativado'}.")
        elif event.key == pygame.K_v: 
            globals.DRAW_VISUAL_RANGE = not globals.DRAW_VISUAL_RANGE
            print(f"P: Desenho do raio de visualização {'ativado' if globals.DRAW_VISUAL_RANGE else 'desativado'}.")

    def _mouse_motion(self, event):
        """
        Manipulador para movimento do mouse.
        """
        if globals.MOUSE_MOTION: 
            globals.MOUSE_POS = event.pos
    
    def _mouse_button_down(self, event):
        """
        Manipulador para botões do mouse pressionados (modo toggle).
        """
        if event.button == 1:
            globals.MOUSE_FEAR = not globals.MOUSE_FEAR
            if globals.MOUSE_FEAR: globals.MOUSE_ATTRACTION = False
            print(f"P: MOUSE_FEAR {'ativado' if globals.MOUSE_FEAR else 'desativado'}.")

        elif event.button == 3: 
            globals.MOUSE_ATTRACTION = not globals.MOUSE_ATTRACTION
            if globals.MOUSE_ATTRACTION: globals.MOUSE_FEAR = False
            print(f"P: MOUSE_ATTRACTION {'ativado' if globals.MOUSE_ATTRACTION else 'desativado'}.")