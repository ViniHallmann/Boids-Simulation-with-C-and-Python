import pygame
import globals
import time
# LER AQUI !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# QUEM NAO LEU, LER: https://vanhunteradams.com/Pico/Animal_Movement/Boids-algorithm.html pelo menos vai entender o que tu ta fazendo.

# O QUE EU VEJO COMO PROXIMOS PASSOS (outras coisas podem aparecer ou serem feitas):
# - REVISAR A UI, MELHORAR A ORGANIZACAO DOS COMPONENTES
#       - Para isso pegar sliders, toggles, buttons e criar componentes que sejam reutilizaveis
#       - Criar uma classe UI que vai orquestrar a organizacao dos componentes,
#         e o renderer vai receber esses componentes e desenhar na tela.

#       - POSSIVEL DEFINICAO:
#           1. DEFINE UM COMPONENTE DE PAINEL NO UI.PY
#           2. UI.PY GERA COMPONENTES DE SLIDERS, BOTOES, ..., GERERICOS BASEADO NO QUE FOR PEDIDO -> botao(nome,cor,funcao,...)
#           3. ADICIONA OS SLIDERS NO PAINEL
#           4. PASSA O PAINEL PRO RENDERER
# - REVISAR A LOGICA DE ATUALIZACAO DOS SLIDERS, TOGGLES E BOTOES

# - REVISAR BOTOES QUE NAO FAZEM NADA
#   - Tem botao que nao faz nada, tem botao que nao tem funcao definida, tem botao que nao faz o que deveria fazer.

# - REVISAR SE ALTERACAO DE VARIAVEIS GLOBAIS ESTA SENDO FEITA DE FORMA CORRETA (TESTAR CADA UMA).
# - REVISAR INPUT DA UI: Estou podendo ativar um botao com o scroll do mouse, isso nao pode acontecer. ATUALIZAR INPUT_HANDLER.
# - IMPLEMENTAR SCROLL VERTICAL NO PAINEL DA UI

# IMPORTANTE: REVISAR ESCALA DOS SLIDERS. TEMOS VARIAVEIS COM VALORES MUITO PEQUENOS(EX. 0.0005) E OUTRAS COM VALORES MUITO GRANDES(EX. 200.0).
# Portanto precisa de uma escala que permita o usuario ajustar esses valores de maneira intuitiva. NAO SEI COMO FAZER ISSO.
# EXEMPLO: Slider protected range nao precisa ser um valor tao grande, seria mais interessante que pudessemos colocar valores menores e mais granulares.

# DICAS DE OTMIZACAO: Cache de Superfícies da UI(gemini q falou):
#   1. Textos Estáticos: Rótulos de sliders e botões que nunca mudam devem ser renderizados com font.render() apenas uma vez e armazenados.
#   2. Textos Dinâmicos (Otimização): Você já fez isso para o contador de FPS! O texto só é renderizado novamente quando o valor muda. 
#       Vamos garantir que todos os textos dinâmicos sigam essa regra.
#   3. Painéis Compostos: O painel da UI, com seu fundo e títulos, deve ser desenhado em uma única superfície (panel_surface) na inicialização. 
#       O loop principal apenas "blita" essa superfície inteira.

#COMPONENTE
class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label, step=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.label = label
        self.step = step
        self.dragging = False
        self.handle_radius = height // 2
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = event.pos[0] - self.rect.x
            rel_x = max(0, min(rel_x, self.rect.width))
            self.val = self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val)
            if self.step:
                self.val = round(self.val / self.step) * self.step

    def draw(self, screen, font):
        # Draw track
        pygame.draw.rect(screen, (60, 60, 60), self.rect, border_radius=self.rect.height // 2)
        
        # Draw handle
        handle_x = self.rect.x + (self.val - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        pygame.draw.circle(screen, (100, 150, 255), (int(handle_x), self.rect.centery), self.handle_radius)
        
        # Draw label and value (reduced spacing)
        label_text = font.render(f"{self.label}: {self.val:.3f}" if self.step is None else f"{self.label}: {int(self.val)}", True, (255, 255, 255))
        screen.blit(label_text, (self.rect.x, self.rect.y - 18))

#COMPONENTE
class ToggleButton:
    def __init__(self, x, y, width, height, label, initial_state=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.state = initial_state
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.state = not self.state
                return True
        return False
                
    def draw(self, screen, font):
        color = (50, 150, 50) if self.state else (150, 50, 50)
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, width=2, border_radius=5)
        
        text = font.render(self.label, True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

#COMPONENTE
class Button:
    def __init__(self, x, y, width, height, label, color=(70, 70, 70)):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.color = color
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False
                
    def draw(self, screen, font):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=5)
        pygame.draw.rect(screen, (100, 100, 100), self.rect, width=2, border_radius=5)
        
        text = font.render(self.label, True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)
####################################################################################
class UI:
    def __init__(self, screen, clock):
        """
        Inicializa os componentes da UI.
        """
        self.font = pygame.font.Font(None, 30)
        self.small_font = pygame.font.Font(None, 18)  # Reduced from 20 to 18 for better spacing
        self.tiny_font = pygame.font.Font(None, 16)   # Added for slider labels
        self.screen = screen
        self.clock = clock
        self.last_fps_text = ""
        self.fps_surface = None
        self.fps_font = pygame.font.Font(None, 30)
        
        # Panel properties
        self.panel_width = 300  # Increased from 280 to give more space
        self.panel_height = screen.get_height()
        self.panel_surface = pygame.Surface((self.panel_width, self.panel_height))
        self.panel_surface.set_alpha(220)
        
        # Initialize sliders and controls
        self.init_controls()
        
        print("P: UI inicializada.")

    def init_controls(self):
        """Inicializa todos os controles da interface"""
        slider_width = 220  # Increased to fit new panel width
        slider_height = 20
        start_x = 40
        current_y = 230  # Start after the headers
        spacing = 35  # Reduced spacing to fit more elements
        
        # Boid Movement sliders
        self.sliders = [
            Slider(start_x, current_y, slider_width, slider_height, 0.0, 1.0, globals.TURN_FACTOR, "turn factor"),
            Slider(start_x, current_y + spacing, slider_width, slider_height, 10.0, 200.0, globals.VISUAL_RANGE, "visual range"), # certo 
            Slider(start_x, current_y + spacing*2, slider_width, slider_height, 5.0, 100.0, globals.PROTECTED_RANGE, "protected range"), # certo 
            Slider(start_x, current_y + spacing*3, slider_width, slider_height, 0.0, 2.0, globals.CENTERING_FACTOR*1000, "cohesion", 0.1), # coesao
            Slider(start_x, current_y + spacing*4, slider_width, slider_height, 0.0, 3.0, globals.AVOID_FACTOR*10, "separation", 0.1), # separacao 
            Slider(start_x, current_y + spacing*5, slider_width, slider_height, 0.0, 2.0, globals.MATCHING_FACTOR*20, "alignment", 0.1), #alinhamento 
            Slider(start_x, current_y + spacing*6, slider_width, slider_height, 1.0, 10.0, globals.MIN_SPEED, "min speed", 1), #pot certo
            Slider(start_x, current_y + spacing*7, slider_width, slider_height, 1.0, 15.0, globals.MAX_SPEED, "max speed", 1), # pot certo 
        ]
        
        # Toggle buttons - positioned after sliders
        toggle_y = current_y + spacing * 8 + 20  # Adjusted for 8 sliders
        self.toggles = [
            ToggleButton(20, toggle_y, 120, 25, "hide menu toggle", False),
            ToggleButton(150, toggle_y, 120, 25, "protected range", globals.DRAW_PROTECTED_RANGE), # PROTECTED E VISUAL RANGE DEVEM SER BOTOES QUE FICAM UM DO LADO DO OUTRO. ELES NAO ESTAO
            ToggleButton(20, toggle_y + 60, 120, 25, "visual range", globals.DRAW_VISUAL_RANGE),
            ToggleButton(20, toggle_y + 30, 120, 25, "complete hide boids", False),
            ToggleButton(150, toggle_y + 30, 120, 25, "change hues to show speed", False),
            ToggleButton(150, toggle_y + 60, 120, 25, "margin", globals.MARGIN_LINE),
            ToggleButton(20, toggle_y + 90, 120, 25, "show debug info", False),
        ]
        
        # Control buttons - positioned after toggles
        button_y = toggle_y + 130
        self.buttons = [
            Button(20, button_y, 80, 30, "restart simulation", (60, 80, 120)),
            Button(110, button_y, 60, 30, "reset settings", (120, 80, 60)),
            Button(180, button_y, 80, 30, "export settings", (80, 120, 60)),
            Button(20, button_y + 40, 80, 30, "import settings", (120, 80, 80)),
        ]
        
        # Boids control buttons - positioned after control buttons
        boids_control_y = button_y + 80
        
        # Boids count slider
        self.boids_slider = Slider(40, boids_control_y + 55, 220, 20, 10, 500, globals.NUM_BIRDS, "boids count", 10)
        
        self.boids_buttons = [
            Button(20, boids_control_y + 25, 60, 25, "- 50", (100, 60, 60)),
            Button(90, boids_control_y + 25, 60, 25, "- 10", (100, 80, 60)),
            Button(160, boids_control_y + 25, 60, 25, "+ 10", (60, 100, 60)),
            Button(230, boids_control_y + 25, 60, 25, "+ 50", (60, 100, 60)),
            Button(20, boids_control_y + 85, 120, 25, "apply new count", (80, 80, 120)),
        ]
        
        # Pause button - positioned separately for easier access
        self.pause_button = Button(20, 110, 100, 25, "pause", (70, 70, 70))
        
        # Debounce timer for boids slider
        self.boids_slider_last_update = 0

    def handle_event(self, event):
        """Handle events for the config panel"""
        if not globals.SHOW_UI_PANEL:
            return False
        
        # Convert mouse coordinates to panel coordinates
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
            panel_x = self.screen.get_width() - self.panel_width
            
            # Check if mouse is within panel area
            if event.pos[0] >= panel_x:
                # Create adjusted coordinates
                adjusted_pos = (event.pos[0] - panel_x, event.pos[1])
                
                # Create a new event with adjusted coordinates by copying the original event
                adjusted_event = pygame.event.Event(event.type, pos=adjusted_pos)
                # Copy other attributes if they exist
                if hasattr(event, 'button'):
                    adjusted_event.button = event.button
                
                # Handle sliders with adjusted coordinates
                for slider in self.sliders:
                    slider.handle_event(adjusted_event)
                
                # Handle boids slider
                self.boids_slider.handle_event(adjusted_event)
                
                # Check if boids slider value changed significantly (debounce)
                current_time = time.time()
                if (abs(int(self.boids_slider.val) - globals.NUM_BIRDS) >= 10 and 
                    current_time - self.boids_slider_last_update > 0.5):  # 500ms debounce
                    self.boids_slider_last_update = current_time
                    
                # Handle toggles with adjusted coordinates
                for toggle in self.toggles:
                    if toggle.handle_event(adjusted_event):
                        self.update_toggle_globals(toggle)
                        
                # Handle buttons with adjusted coordinates
                for button in self.buttons:
                    if button.handle_event(adjusted_event):
                        self.handle_button_action(button.label)
                
                # Handle boids control buttons with adjusted coordinates
                for button in self.boids_buttons:
                    if button.handle_event(adjusted_event):
                        self.handle_boids_button_action(button.label)
                
                # Handle pause button with adjusted coordinates
                if self.pause_button.handle_event(adjusted_event):
                    self.toggle_pause()
                
                # Update globals from sliders
                self.update_slider_globals()
                return True  # Event was handled
        
        return False  # Event was not handled

    def update_slider_globals(self):
        """Update global variables from slider values"""    
        if len(self.sliders) >= 7:  # Updated to match current number of sliders
            globals.TURN_FACTOR = self.sliders[0].val
            globals.VISUAL_RANGE = self.sliders[1].val
            globals.PROTECTED_RANGE = self.sliders[2].val
            globals.CENTERING_FACTOR = self.sliders[3].val / 1000
            globals.AVOID_FACTOR = self.sliders[4].val / 10
            globals.MATCHING_FACTOR = self.sliders[5].val / 20
            globals.MIN_SPEED = self.sliders[6].val  # Updated index
            globals.MAX_SPEED = self.sliders[7].val  # Updated index


    # ELE ATUALIZA AS VARAIVEIS GLOBAIS BASEADA NA LABEL DO TOGGLE
    # NAO GOSTO DISSO POIS AO MUDAR O NOME DA LABEL O CODIGO QUEBRA,
    # PENSAR EM OUTRA MANEIRA DE ATUALIZAR AS VARIAVEIS GLOBAIS COM A ACAO DO TOGGLE
    def update_toggle_globals(self, toggle):
        """Update global variables from toggle states"""
        if toggle.label == "protected range":
            globals.DRAW_PROTECTED_RANGE = toggle.state
        elif toggle.label == "visual range":
            globals.DRAW_VISUAL_RANGE = toggle.state
        elif toggle.label == "margin":
            globals.MARGIN_LINE = toggle.state

    def handle_button_action(self, action):
        """Handle button actions"""
        if action == "restart simulation":
            self.restart_simulation()
        elif action == "reset settings":
            self.reset_to_defaults()                                                                                                                                        
        elif action == "export settings":
            print("Export settings requested")
        elif action == "import settings":
            print("Import settings requested")

    # NAO GOSTEI DISSO AQUI
    # Eu faco o restart_simulation dentro da propria UI.py
    def handle_boids_button_action(self, action):
        """Handle boids control button actions"""
        current_boids = globals.NUM_BIRDS
        new_boids = current_boids
        
        if action == "- 50":
            new_boids = max(10, current_boids - 50)  # Minimum 10 boids
        elif action == "- 10":
            new_boids = max(10, current_boids - 10)
        elif action == "+ 10":
            new_boids = min(1000, current_boids + 10)  # Maximum 1000 boids
        elif action == "+ 50":
            new_boids = min(1000, current_boids + 50)
        elif action == "apply new count":
            new_boids = int(self.boids_slider.val)
        
        if new_boids != current_boids:
            restart_event = pygame.event.Event(pygame.USEREVENT, 
                action="restart_simulation", 
                num_birds=new_boids
            )
            pygame.event.post(restart_event)

    # POR QUE TEM UM RESTART SIMULATION E UM RESTART SIMULATION WITH BOIDS AQUI? MESMA CHAMADA NO APP.PY
    # MELHORAR
    # PRECISA TIPAR ...
    def restart_simulation(self, new_num_birds=None):
        """Request simulation restart through the app instance"""
        # We need a way to communicate with the app instance
        # For now, we'll set a flag that the app can check
        #restar_simulation_with_boids EH UM BOOLEANDO, POR QUE ESTA RECEBENDO UM NUMERO DE BOIDS?
        if new_num_birds is not None:
            globals.RESTART_SIMULATION_WITH_BOIDS = new_num_birds
        else:
            globals.RESTART_SIMULATION = True

    def toggle_pause(self):
        """Toggle pause state and update button label"""
        globals.PAUSED = not globals.PAUSED
        self.update_pause_button_state()
        if globals.PAUSED:
            print("P: Simulação pausada.")
        else:
            print("P: Simulação retomada.")

    def update_pause_button_state(self):
        """Update pause button appearance based on current pause state"""
        if globals.PAUSED:
            self.pause_button.label = "▶  play"
            self.pause_button.color = (50, 120, 50)  # Green for play
        else:
            self.pause_button.label = "❚❚  pause"
            self.pause_button.color = (120, 50, 50)  # Red for pause

    def reset_to_defaults(self):
        """Reset all settings to default values"""
        # Reset slider values to defaults
        defaults = [0.2, 75.0, 35.0, 0.5, 1.0, 1.0, 1.1, 0.2, 3.0, 6.0, 0.005, 1.0]
        for i, default in enumerate(defaults):
            if i < len(self.sliders):
                self.sliders[i].val = default
        
        # Reset toggles
        for toggle in self.toggles:
            toggle.state = False
            
        self.update_slider_globals()

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
        
        if self.fps_surface: 
            self.screen.blit(self.fps_surface, (10, 10))

    def draw_config_panel(self):
        """Draw the configuration panel"""
        if not globals.SHOW_UI_PANEL:
            return
            
        # Clear panel
        self.panel_surface.fill((20, 25, 35))
        
        # Draw title
        title = self.font.render("boids", True, (100, 150, 255))
        self.panel_surface.blit(title, (20, 10))
        
        subtitle = self.small_font.render("source:code", True, (150, 150, 150))
        self.panel_surface.blit(subtitle, (80, 15))
        
        # Instructions
        instructions = [
            "left and right click to move the boids, or just watch their",
            "flocking patterns!",
            "double click or click in the top right to toggle this menu",
            "press space or click pause button to pause simulation"
        ]
        
        y_offset = 40
        for instruction in instructions:
            text = self.small_font.render(instruction, True, (180, 180, 180))
            self.panel_surface.blit(text, (15, y_offset))
            y_offset += 15
            
        # Draw pause/play button
        self.update_pause_button_state()  # Ensure button state is current
        self.pause_button.draw(self.panel_surface, self.small_font)
        
        # Section headers
        visual_header = self.font.render("visual settings", True, (255, 255, 255))
        self.panel_surface.blit(visual_header, (20, 170))
        
        movement_header = self.font.render("boid movement", True, (255, 255, 255))
        self.panel_surface.blit(movement_header, (20, 200))
        
        # Draw sliders
        for slider in self.sliders:
            slider.draw(self.panel_surface, self.tiny_font)  # Use smaller font for slider labels
            
        # Draw toggles section header
        toggles_y = 230 + 35 * 8 + 20  # Adjusted for 8 sliders
        toggles_header = self.font.render("display options", True, (255, 255, 255))
        self.panel_surface.blit(toggles_header, (20, toggles_y - 25))
            
        # Draw toggles
        for toggle in self.toggles:
            toggle.draw(self.panel_surface, self.small_font)
            
        # Draw buttons section header
        buttons_y = toggles_y + 130  # Same calculation as in init_controls
        buttons_header = self.font.render("controls", True, (255, 255, 255))
        self.panel_surface.blit(buttons_header, (20, buttons_y - 25))
            
        # Draw buttons
        for button in self.buttons:
            button.draw(self.panel_surface, self.small_font)
            
        # Draw boids control section header
        boids_control_y = buttons_y + 80
        boids_header = self.font.render("boids count", True, (255, 255, 255))
        self.panel_surface.blit(boids_header, (20, boids_control_y - 25))
        
        # Show current number of boids
        current_boids_text = self.small_font.render(f"current: {globals.NUM_BIRDS} boids", True, (180, 180, 180))
        self.panel_surface.blit(current_boids_text, (20, boids_control_y))
        
        # Draw boids control buttons
        for button in self.boids_buttons:
            button.draw(self.panel_surface, self.tiny_font)
            
        # Draw boids slider
        self.boids_slider.draw(self.panel_surface, self.tiny_font)
            
        # Blit panel to screen
        self.screen.blit(self.panel_surface, (self.screen.get_width() - self.panel_width, 0))

    def draw(self):
        """Main draw method"""
        self.draw_fps()
        self.draw_config_panel()
        
    def get_panel_rect(self):
        """Returns the panel rectangle for collision detection"""
        panel_x = self.screen.get_width() - self.panel_width
        return pygame.Rect(panel_x, 0, self.panel_width, self.panel_height)