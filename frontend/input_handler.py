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
            
            ui_handled = self.app.renderer.UI.handle_event(event)
            
            if not ui_handled:
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
            pygame.USEREVENT: self._user_event_handler
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
            print("P: Aplicação encerrada com Q.")
        elif event.key == pygame.K_ESCAPE:
            self.app.running = False
            print("P: Aplicação encerrada com ESC.")
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
        elif event.key == pygame.K_d:
            globals.DRAW_PROTECTED_RANGE = True
            globals.DRAW_VISUAL_RANGE = True
            print("P: Modo debug ativado.")
        elif event.key == pygame.K_f:
            globals.DRAW_PROTECTED_RANGE = False
            globals.DRAW_VISUAL_RANGE = False
            print("P: Modo debug desativado.")
        elif event.key == pygame.K_h: # HIDE UI
            globals.SHOW_UI_PANEL = not globals.SHOW_UI_PANEL
            print(f"P: Painel da UI {'visível' if globals.SHOW_UI_PANEL else 'oculto'}.")
        elif event.key == pygame.K_SPACE: # PAUSE/PLAY
            globals.PAUSED = not globals.PAUSED
            print(f"P: Simulação {'pausada' if globals.PAUSED else 'retomada'}.")
        elif event.key == pygame.K_6:
            globals.BOUNDARY_BEHAVIOR = globals.BoundaryBehavior.BOUNDARY_TURN
            print("P: Comportamento de limite: TURN.")
        elif event.key == pygame.K_7:
            globals.BOUNDARY_BEHAVIOR = globals.BoundaryBehavior.BOUNDARY_BOUNCE
            print("P: Comportamento de limite: BOUNCE.")
        elif event.key == pygame.K_8:
            globals.BOUNDARY_BEHAVIOR = globals.BoundaryBehavior.BOUNDARY_WRAP
            print("P: Comportamento de limite: WRAP.")

    def _mouse_motion(self, event):
        """
        Manipulador para movimento do mouse.
        """
        if globals.MOUSE_MOTION: 
            globals.MOUSE_POS = event.pos
    
    def _mouse_button_down(self, event):
        """
        Manipulador para botões do mouse.
        O clique esquerdo alterna o modo 'medo'. O direito não faz nada.
        """
        if event.button == 1: # Clique Esquerdo
            globals.MOUSE_FEAR = not globals.MOUSE_FEAR
            if globals.MOUSE_FEAR:
                globals.MOUSE_ATTRACTION = False
            print(f"P: MOUSE_FEAR {'ativado' if globals.MOUSE_FEAR else 'desativado'}.")

    def _user_event_handler(self, event):
        """
        Manipulador para eventos personalizados (USEREVENT).
        Distribui o evento para o método correto baseado no tipo de ação.
        """
        if event.action == "restart_simulation":
            self.app.restart_simulation(event.num_birds)
        else:
            print(f"P: Evento desconhecido: {event.action}")