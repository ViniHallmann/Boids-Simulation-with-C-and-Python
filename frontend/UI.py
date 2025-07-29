import pygame
import globals
import time
import json
import os

# --- COMPONENTES DA UI REUTILIZÁVEIS ---

class Slider:
    def __init__(self, label, min_val, max_val, initial_val, callback, value_factor=1.0, step=None):
        self.last_value_text = ""
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.callback = callback
        self.value_factor = value_factor
        self.step = step

        self.handle_radius  = 0
        self.dragging       = False
        self.rect           = None
        self.font_surface   = None
        self.value_surface  = None

    def layout(self, x, y, width, height, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.handle_radius = max(6, height // 3)  # Menor e com tamanho mínimo
        label_text = f"{self.label}:"
        self.font_surface = font.render(label_text, True, (180, 190, 210))

    #isso aqui funciona MAS acho que da pra integrar com o input_handler.py e fazer com que ele lide com esses evento.
    #att: posso fazer isso, mas acho que assim é mais escalável deixa cada componente gerenciando os próprios eventos.
    def handle_event(self, event):
        if not hasattr(event, 'pos'): return False
        if self.min_val >= self.max_val: return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self._update_value_from_pos(event.pos)
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_value_from_pos(event.pos)
            return True
        return False

    def _update_value_from_pos(self, pos):
        rel_x = max(0, min(pos[0] - self.rect.x, self.rect.width))
        self.val = self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val)
        if self.step:
            self.val = round(self.val / self.step) * self.step
        self.callback(self.val * self.value_factor)

    def draw(self, surface, font):
        surface.blit(self.font_surface, (self.rect.x, self.rect.y - 15))
        display_val = self.val * self.value_factor
        current_value_text = f"{display_val:.3f}" if isinstance(display_val, float) and self.step is None else f"{int(display_val)}"
        if current_value_text != self.last_value_text:
            self.last_value_text = current_value_text
            self.value_surface = font.render(current_value_text, True, (255, 255, 255))

        if self.value_surface:
            surface.blit(self.value_surface, (self.rect.right - self.value_surface.get_width(), self.rect.y - 18))
        
        pygame.draw.rect(surface, (40, 45, 60), self.rect, border_radius=self.rect.height // 2)

        if self.max_val > self.min_val:
            handle_x = self.rect.x + (self.val - self.min_val) / (self.max_val - self.min_val) * self.rect.width
            pygame.draw.circle(surface, (166, 181, 176), (int(handle_x), self.rect.centery), self.handle_radius + 1)
        else:
            pygame.draw.circle(surface, (100, 150, 255), (self.rect.x, self.rect.centery), self.handle_radius + 1)


class Button:
    def __init__(self, label, callback, color=(70, 70, 70)):
        self.label = label
        self.callback = callback
        self.color = color
        self.hover_color = tuple(min(c + 25, 255) for c in color)
        self.hovering = False
        self.rect = None
        self.font = None
        self.font_surface  = None
        self.border_radius: int = 12
        self.width: int = 2

    def layout(self, x, y, width, height, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.font_surface = self.font.render(self.label, True, (255, 255, 255))

    def handle_event(self, event):
        if not hasattr(event, 'pos'): return False
        if self.rect.collidepoint(event.pos):
            self.hovering = True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.callback()
                return True
        else:
            self.hovering = False
        return False

    def draw(self, surface):
        color = self.hover_color if self.hovering else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, (100, 100, 100), self.rect, width=self.width, border_radius=self.border_radius - 3)
        text_rect = self.font_surface.get_rect(center=self.rect.center)
        surface.blit(self.font_surface, text_rect)

class ToggleButton(Button):
    def __init__(self, label, initial_state, callback):
        self.state = initial_state
        self.state_callback = callback
        super().__init__(label, lambda: self.toggle(), color=self.get_color())
        self.state_callback(self.state)

    def toggle(self):
        self.state = not self.state
        self.color = self.get_color()
        self.hover_color = tuple(min(c + 25, 255) for c in self.color)
        self.state_callback(self.state)

    def get_color(self):
        return (50, 150, 50) if self.state else (150, 50, 50)

    def draw(self, surface):
        if self.font:
            self.font_surface = self.font.render(self.label, True, (255, 255, 255))
        
        super().draw(surface)

# --- UI MANAGER CLASS ---

class UI:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.controls = []
        self.input_handler = None  # Referência para o input_handler
        
        self.font_large  = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small  = pygame.font.Font(None, 18)
        self.font_tiny   = pygame.font.Font(None, 16)

        self.last_fps_text = ""
        self.fps_surface = None

        self.panel_width  = 320
        self.panel_height = screen.get_height()

        self.visible_x = self.screen.get_width() - self.panel_width
        self.hidden_x  = self.screen.get_width()
        self.target_x  = self.hidden_x
        self.current_x = float(self.hidden_x)

        self.animation_speed = 0.15

        self.visible_panel = pygame.Surface((self.panel_width, self.panel_height))
        self.visible_panel.set_alpha(245)
        self.panel_rect = self.visible_panel.get_rect(topleft=(self.current_x, 0))
        globals.UI_PANEL_RECT = self.panel_rect

        self.content_surface = None
        self.content_height = 0
        self.scroll_offset_y = 0
        self.scroll_speed = 40

        self.header_surfaces = {}

        self.toggle_button_font = pygame.font.Font(None, 50)
        self.show_panel_surf = self.toggle_button_font.render("‹", True, (200, 200, 200))
        self.hide_panel_surf = self.toggle_button_font.render("›", True, (200, 200, 200))
        self.toggle_button_rect = self.show_panel_surf.get_rect() 

        self.staged_boid_count = globals.NUM_BIRDS
        
        self.settings_dir = "settings"
        self.settings_filepath = os.path.join(self.settings_dir, "settings.json")

        self.init_controls()
        self.content_height = self._layout_controls()
        self.content_surface = pygame.Surface((self.panel_width, self.content_height))

        print("P: UI inicializada com sucesso (versão com Import/Export).")

    def set_input_handler_reference(self, input_handler):
        """Define a referência ao input_handler para comunicação bidirecional."""
        self.input_handler = input_handler

    def _update_max_speed(self, new_max_speed):
        """Callback para o slider de Max Speed."""
        globals.MAX_SPEED = new_max_speed
        self.min_speed_slider.max_val = new_max_speed

        if self.min_speed_slider.val > new_max_speed:
            self.min_speed_slider.val = new_max_speed
            globals.MIN_SPEED = new_max_speed

    def _update_min_speed(self, new_min_speed):
        """Callback para o slider de Min Speed."""
        globals.MIN_SPEED = new_min_speed
        self.max_speed_slider.min_val = new_min_speed
        if self.max_speed_slider.val < new_min_speed:
            self.max_speed_slider.val = new_min_speed
            globals.MAX_SPEED = new_min_speed

    def _export_settings(self):
        """Coleta as configurações atuais e as salva em um arquivo JSON."""
        print(f"P: Exportando configurações para {self.settings_filepath}...")
        
        settings_data = {}
        for control in self.controls:
            if isinstance(control, Slider):
                real_value = control.val * control.value_factor if hasattr(control, 'value_factor') else control.val
                settings_data[control.label] = real_value
            elif isinstance(control, ToggleButton):
                 settings_data[control.label] = control.state
        
        settings_data["Boids Count"] = self.staged_boid_count
        
        try:
            os.makedirs(self.settings_dir, exist_ok=True)
            with open(self.settings_filepath, 'w') as f:
                json.dump(settings_data, f, indent=4)
            print("P: Configurações exportadas com sucesso.")
        except Exception as e:
            print(f"ERRO: Falha ao exportar configurações: {e}")

    def _import_settings(self):
        """Carrega as configurações de um arquivo JSON e atualiza a UI."""
        print(f"P: Importando configurações de {self.settings_filepath}...")
        
        if not os.path.exists(self.settings_filepath):
            print(f"ERRO: Arquivo de configurações não encontrado em {self.settings_filepath}")
            return
            
        try:
            with open(self.settings_filepath, 'r') as f:
                loaded_data = json.load(f)
            
            for control in self.controls:
                if isinstance(control, Slider) and control.label in loaded_data:
                    loaded_value = loaded_data[control.label]
                    control.val = loaded_value / control.value_factor if hasattr(control, 'value_factor') and control.value_factor != 0 else loaded_value
                    control.callback(loaded_value)
                elif isinstance(control, ToggleButton) and control.label in loaded_data:
                    loaded_state = loaded_data[control.label]
                    if control.state != loaded_state:
                         control.toggle()


            if "Boids Count" in loaded_data:
                self.staged_boid_count = loaded_data["Boids Count"]
                self.boid_count_slider.val = self.staged_boid_count
                self.boid_count_slider.callback(self.staged_boid_count)

            print("P: Configurações importadas. Clique em 'Apply Count & Restart' para aplicar as mudanças.")

        except Exception as e:
            print(f"ERRO: Falha ao importar configurações: {e}")

    def _layout_controls(self):
        """
        Calcula a posição de todos os controles e textos estáticos uma única vez.
        Retorna a altura total do conteúdo.
        """
        x_margin = 10
        scrollbar_gutter = 20
        content_width = self.panel_width - x_margin - scrollbar_gutter
        y_cursor = 20
        
        # Pré-renderiza e armazena posições de textos estáticos
        self.static_surfaces = []
        title_surf = self.font_large.render("Boids Controls", True, (120, 170, 255))
        self.static_surfaces.append((title_surf, (x_margin, y_cursor)))
        y_cursor += 50

        instructions = [
            "Move the mouse around or just watch them flock.",
            "Left-click to toggle fear mode on/off.",
            "Right-click to toggle attraction mode on/off.",
            "Press 'H' or click the side tab to toggle this menu.",
            "Press Spacebar or the Pause button to pause."
        ]
        for line in instructions:
            instruction_surf = self.font_small.render(line, True, (180, 180, 180))
            self.static_surfaces.append((instruction_surf, (x_margin, y_cursor)))
            y_cursor += 20 
        y_cursor += 20

        # Layout dos botões principais
        button_height = 35
        button_width = (content_width) / 2 - 5
        self.main_buttons[0].layout(x_margin, y_cursor, button_width, button_height, self.font_medium)
        self.main_buttons[1].layout(x_margin + button_width + 10, y_cursor, button_width, button_height, self.font_medium)
        y_cursor += 40
        self.main_buttons[2].layout(x_margin, y_cursor, button_width, button_height, self.font_medium)
        self.main_buttons[3].layout(x_margin + button_width + 10, y_cursor, button_width, button_height, self.font_medium)
        y_cursor += 45
        self.main_buttons[4].layout(x_margin, y_cursor, content_width, button_height + 5, self.font_medium)
        y_cursor += 50

        # Layout das seções
        def layout_section(title, controls, start_y, spacing, font, layout_func):
            start_y += 5
            header_surf = font.render(title, True, (180, 190, 210))
            self.static_surfaces.append((header_surf, (x_margin, start_y)))
            y = start_y + 40
            for control in controls:
                layout_func(control, y)
                y += spacing
            return y
        
        slider_layout = lambda ctrl, y: ctrl.layout(x_margin, y, content_width, 15, self.font_tiny)
        y_cursor = layout_section("Behavior", self.sliders, y_cursor, 35, self.font_medium, slider_layout)
        y_cursor = layout_section("Display", self.display_sliders, y_cursor, 35, self.font_medium, slider_layout)
        
        y_cursor += 5
        header_surf = self.font_medium.render("Boundary Behavior", True, (220, 220, 220))
        self.static_surfaces.append((header_surf, (x_margin, y_cursor)))
        y_cursor += 40
        
        button_width_bh = (content_width) / 3 - 8
        for i, btn in enumerate(self.behavior_buttons):
            btn.layout(x_margin + i * (button_width_bh + 10), y_cursor, button_width_bh, 30, self.font_small)

        y_cursor += 50
        header_surf = self.font_medium.render("Debug Toggles", True, (220, 220, 220))
        self.static_surfaces.append((header_surf, (x_margin, y_cursor)))
        toggle_y = y_cursor + 40
        
        toggle_width = (content_width - 10) / 2
        for i, toggle in enumerate(self.toggles):
            row, col = divmod(i, 2)
            x_pos = x_margin + col * (toggle_width + 10)
            y_pos = toggle_y + row * 40
            toggle.layout(x_pos, y_pos, toggle_width, 30, self.font_small)
        num_toggle_rows = (len(self.toggles) + 1) // 2
        y_cursor = toggle_y + num_toggle_rows * 40

        y_cursor += 15
        header_surf = self.font_medium.render("Population", True, (220, 220, 220))
        self.static_surfaces.append((header_surf, (x_margin, y_cursor)))
        y_cursor += 25 
        
        self.boid_count_slider.layout(x_margin, y_cursor + 20, content_width, 20, self.font_tiny)
        y_cursor += 35 + 20
        self.apply_boids_button.layout(x_margin, y_cursor, content_width, 35, self.font_medium)
        y_cursor += 50
        
        return y_cursor

    def init_controls(self):
        self.controls = []
        self.min_speed_slider = Slider(
            "Min Speed", 1.0, 15.0, globals.DEFAULT_SETTINGS["MIN_SPEED"], 
            self._update_min_speed, step=0.5
        )
        self.max_speed_slider = Slider(
            "Max Speed", 1.0, 15.0, globals.DEFAULT_SETTINGS["MAX_SPEED"], 
            self._update_max_speed, step=0.5
        )
        
        self._update_max_speed(self.max_speed_slider.val)
        self._update_min_speed(self.min_speed_slider.val)

        self.sliders = [
            Slider("Turn Factor", 0.0, 1.0, globals.DEFAULT_SETTINGS["TURN_FACTOR"], lambda v: setattr(globals, 'TURN_FACTOR', v)),
            Slider("Cohesion", 0.0, 150.0, globals.DEFAULT_SETTINGS["CENTERING_FACTOR"] * 4000, lambda v: setattr(globals, 'CENTERING_FACTOR', v), value_factor=0.00025),
            Slider("Separation", 0.0, 3.0, globals.DEFAULT_SETTINGS["AVOID_FACTOR"] * 10, lambda v: setattr(globals, 'AVOID_FACTOR', v), value_factor=0.1),
            Slider("Alignment", 0.0, 8.0, globals.DEFAULT_SETTINGS["MATCHING_FACTOR"] * 20, lambda v: setattr(globals, 'MATCHING_FACTOR', v), value_factor=0.05),
            self.min_speed_slider,
            self.max_speed_slider  
        ]
        self.controls.extend(self.sliders)
        
        self.display_sliders = [
            Slider("Visual Range", 10.0, 200.0, globals.DEFAULT_SETTINGS["VISUAL_RANGE"], lambda v: setattr(globals, 'VISUAL_RANGE', v), step=1),
            Slider("Protected Range", 5.0, 100.0, globals.DEFAULT_SETTINGS["PROTECTED_RANGE"], lambda v: setattr(globals, 'PROTECTED_RANGE', v), step=1),
        ]
        self.controls.extend(self.display_sliders)
        
        self.toggles = [
            ToggleButton("Mouse Influence", globals.MOUSE_MOTION, lambda s: setattr(globals, 'MOUSE_MOTION', s)),
            ToggleButton("Margin", globals.MARGIN_LINE, self._handle_margin_toggle),
            ToggleButton("Visual Range", globals.DRAW_VISUAL_RANGE, lambda s: setattr(globals, 'DRAW_VISUAL_RANGE', s)),
            ToggleButton("Protected Range", globals.DRAW_PROTECTED_RANGE, lambda s: setattr(globals, 'DRAW_PROTECTED_RANGE', s)),
            ToggleButton("Dynamic Colors", globals.DYNAMIC_COLOR_ENABLED, lambda s: setattr(globals, 'DYNAMIC_COLOR_ENABLED', s)),
        ]
        self.controls.extend(self.toggles)

        self.boid_count_slider = Slider("Boids Count", 10, 5000, self.staged_boid_count, lambda v: setattr(self, 'staged_boid_count', v), step=10)
        self.controls.append(self.boid_count_slider)
        
        self.apply_boids_button = Button("Apply Count & Restart", self.post_restart_event, color=(60, 100, 140))
        self.controls.append(self.apply_boids_button)

        self.behavior_buttons = [
            Button("Turn", lambda: self._set_boundary_behavior(globals.BoundaryBehavior.BOUNDARY_TURN)),
            Button("Bounce", lambda: self._set_boundary_behavior(globals.BoundaryBehavior.BOUNDARY_BOUNCE)),
            Button("Wrap", lambda: self._set_boundary_behavior(globals.BoundaryBehavior.BOUNDARY_WRAP))
        ]
        self.controls.extend(self.behavior_buttons)
        self._update_behavior_button_colors()
        # Atualiza o estado da margin baseado no comportamento inicial
        self._update_margin_toggle_based_on_behavior(globals.BOUNDARY_BEHAVIOR)

        self.main_buttons = [
            Button("Pause", self.toggle_pause, color=(120, 50, 50)),
            Button("Reset", self.reset_to_defaults, color=(180, 90, 80)),
            Button("Export", self._export_settings, color=(60, 70, 90)),
            Button("Import", self._import_settings, color=(60, 70, 90)),
            Button("Restart", self.post_restart_event, color=(60, 80, 120))
        ]
        self.controls.extend(self.main_buttons)
        self.pause_button = self.main_buttons[0]
        self.update_pause_button_state()

    def _draw_scrollbar(self):
        if self.content_height <= self.panel_height:
            return

        track_height = self.panel_height - 20
        track_rect = pygame.Rect(self.panel_width - 12, 10, 8, track_height)
        pygame.draw.rect(self.visible_panel, (40, 40, 50), track_rect, border_radius=4)

        handle_height = track_height * (self.panel_height / self.content_height)
        handle_height = max(handle_height, 20)

        max_scroll = self.content_height - self.panel_height
        scroll_ratio = self.scroll_offset_y / max_scroll if max_scroll > 0 else 0
        
        handle_y = track_rect.y + scroll_ratio * (track_height - handle_height)
        handle_rect = pygame.Rect(track_rect.x, handle_y, track_rect.width, handle_height)
        pygame.draw.rect(self.visible_panel, (100, 110, 120), handle_rect, border_radius=4)
        
    def post_restart_event(self):
        restart_event = pygame.event.Event(pygame.USEREVENT,
            action="restart_simulation",
            num_birds=int(self.staged_boid_count)
        )
        pygame.event.post(restart_event)

    def reset_to_defaults(self):
        print("P: Resetting UI controls to default values (no restart).")
        for control in self.controls:
            if isinstance(control, Slider):
                key_map = {
                    "Turn Factor": "TURN_FACTOR", "Cohesion": "CENTERING_FACTOR", "Separation": "AVOID_FACTOR",
                    "Alignment": "MATCHING_FACTOR", "Min Speed": "MIN_SPEED", "Max Speed": "MAX_SPEED",
                    "Visual Range": "VISUAL_RANGE", "Protected Range": "PROTECTED_RANGE", "Boids Count": "NUM_BIRDS"
                }
                if control.label in key_map:
                    key = key_map[control.label]
                    default_val = globals.DEFAULT_SETTINGS[key]
                    control.val = default_val / control.value_factor if hasattr(control, 'value_factor') and control.value_factor != 1.0 else default_val
                    control.callback(control.val * control.value_factor)
            
            elif isinstance(control, ToggleButton):
                key_map = {
                    "Mouse Influence": "MOUSE_MOTION", "Show Margin": "MARGIN_LINE", 
                    "Show Visual Range": "DRAW_VISUAL_RANGE", "Show Protected Range": "DRAW_PROTECTED_RANGE",
                    "Dynamic Colors": "DYNAMIC_COLOR_ENABLED"
                }
                if control.label in key_map:
                    key = key_map[control.label]
                    default_state = globals.DEFAULT_SETTINGS[key]
                    if control.state != default_state:
                        control.toggle()
        
        self.staged_boid_count = globals.DEFAULT_SETTINGS["NUM_BIRDS"]
        if self.boid_count_slider.val != self.staged_boid_count:
             self.boid_count_slider.val = self.staged_boid_count
             self.boid_count_slider.callback(self.staged_boid_count)
        
        # Atualiza as cores dos botões de comportamento
        self._update_behavior_button_colors()
        # Atualiza o estado da margin baseado no comportamento atual
        self._update_margin_toggle_based_on_behavior(globals.BOUNDARY_BEHAVIOR)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.toggle_button_rect.collidepoint(event.pos):
                globals.SHOW_UI_PANEL = not globals.SHOW_UI_PANEL
                return True
        if not globals.SHOW_UI_PANEL:
            return False

        if not hasattr(event, 'pos'):
            return False

        if not self.panel_rect.collidepoint(event.pos):
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            max_scroll = self.content_height - self.panel_height
            if max_scroll > 0:
                if event.button == 4:
                    self.scroll_offset_y = max(0, self.scroll_offset_y - self.scroll_speed)
                    return True
                elif event.button == 5:
                    self.scroll_offset_y = min(max_scroll, self.scroll_offset_y + self.scroll_speed)
                    return True

        adj_pos = (event.pos[0] - self.panel_rect.x, event.pos[1] + self.scroll_offset_y)
        adj_event = pygame.event.Event(event.type, pos=adj_pos, button=getattr(event, 'button', 0))

        for control in self.controls:
            if control.handle_event(adj_event):
                return True
        return True

    def toggle_pause(self):
        globals.PAUSED = not globals.PAUSED
        self.update_pause_button_state()

    def update_pause_button_state(self):
        if globals.PAUSED:
            self.pause_button.label = "Play"
            self.pause_button.color = (50, 120, 50)
        else:
            self.pause_button.label = "Pause"
            self.pause_button.color = (120, 50, 50)
        self.pause_button.hover_color = tuple(min(c + 25, 255) for c in self.pause_button.color)
        self.pause_button.font_surface = self.font_medium.render(self.pause_button.label, True, (255, 255, 255))

    def _set_boundary_behavior(self, behavior):
        """Define o comportamento de fronteira e atualiza as cores dos botões."""
        globals.BOUNDARY_BEHAVIOR = behavior
        self._update_behavior_button_colors()
        self._update_margin_toggle_based_on_behavior(behavior)

    def _update_behavior_button_colors(self):
        """Atualiza as cores dos botões de comportamento baseado no estado atual."""
        current_behavior = globals.BOUNDARY_BEHAVIOR
        
        # Mapeia cada botão ao seu comportamento correspondente
        behavior_map = [
            globals.BoundaryBehavior.BOUNDARY_TURN,
            globals.BoundaryBehavior.BOUNDARY_BOUNCE,
            globals.BoundaryBehavior.BOUNDARY_WRAP
        ]
        
        for i, button in enumerate(self.behavior_buttons):
            if behavior_map[i] == current_behavior:
                # Botão ativo - verde
                button.color = (50, 120, 50)
            else:
                # Botões inativos - vermelho
                button.color = (120, 50, 50)
            
            # Atualiza a cor de hover
            button.hover_color = tuple(min(c + 25, 255) for c in button.color)
            
            # Re-renderiza o texto se o botão já foi layoutado
            if button.font:
                button.font_surface = button.font.render(button.label, True, (255, 255, 255))

    def _update_margin_toggle_based_on_behavior(self, behavior):
        """Atualiza o estado do toggle de margin baseado no comportamento de fronteira."""
        # Encontra o toggle de margin
        margin_toggle = None
        for toggle in self.toggles:
            if toggle.label == "Margin":
                margin_toggle = toggle
                break
        
        if margin_toggle:
            # Se for BOUNCE ou WRAP, desabilita a margin
            if behavior in [globals.BoundaryBehavior.BOUNDARY_BOUNCE, globals.BoundaryBehavior.BOUNDARY_WRAP]:
                if margin_toggle.state:  # Se estava ativado, desativa
                    margin_toggle.toggle()
            # Se for TURN, não força nenhum estado (deixa o usuário controlar)

    def _handle_margin_toggle(self, state):
        """Callback customizado para o toggle de margin que verifica o comportamento."""
        # Só permite ativar margin se o comportamento for TURN
        if state and globals.BOUNDARY_BEHAVIOR != globals.BoundaryBehavior.BOUNDARY_TURN:
            print("P: Margin só pode ser ativada no modo TURN")
            # Encontra o toggle de margin e força o estado para False
            for toggle in self.toggles:
                if toggle.label == "Margin":
                    if toggle.state:  # Se estava ativado, desativa
                        toggle.state = False
                        toggle.color = toggle.get_color()
                        toggle.hover_color = tuple(min(c + 25, 255) for c in toggle.color)
                    break
            return  # Não altera o estado global se não for permitido
        
        globals.MARGIN_LINE = state

    def sync_toggles_with_globals(self):
        """Sincroniza o estado dos toggles com as variáveis globais."""
        toggle_map = {
            "Mouse Influence": globals.MOUSE_MOTION,
            "Margin": globals.MARGIN_LINE,
            "Visual Range": globals.DRAW_VISUAL_RANGE,
            "Protected Range": globals.DRAW_PROTECTED_RANGE,
            "Dynamic Colors": globals.DYNAMIC_COLOR_ENABLED
        }
        
        for toggle in self.toggles:
            if toggle.label in toggle_map:
                expected_state = toggle_map[toggle.label]
                if toggle.state != expected_state:
                    # Atualiza silenciosamente sem chamar o callback
                    toggle.state = expected_state
                    toggle.color = toggle.get_color()
                    toggle.hover_color = tuple(min(c + 25, 255) for c in toggle.color)
                    if toggle.font:
                        toggle.font_surface = toggle.font.render(toggle.label, True, (255, 255, 255))

    def sync_behavior_buttons_with_globals(self):
        """Sincroniza o estado dos botões de comportamento com as variáveis globais."""
        self._update_behavior_button_colors()
        self._update_margin_toggle_based_on_behavior(globals.BOUNDARY_BEHAVIOR)

    def sync_pause_button_with_globals(self):
        """Sincroniza o estado do botão de pause com as variáveis globais."""
        self.update_pause_button_state()

    def sync_all_with_globals(self):
        """Sincroniza todos os componentes da UI com as variáveis globais."""
        self.sync_toggles_with_globals()
        self.sync_behavior_buttons_with_globals()
        self.sync_pause_button_with_globals()
        
        
        
    def draw_fps(self):
        current_fps_text = f"FPS: {self.clock.get_fps():.0f}"
        if current_fps_text != self.last_fps_text:
            self.last_fps_text = current_fps_text
            self.fps_surface = self.font_medium.render(current_fps_text, True, (255, 255, 255))
        if self.fps_surface:
            self.screen.blit(self.fps_surface, (10, 10))

    def _draw_toggle_button(self):
        """Desenha o botão de mostrar/esconder o painel."""
        panel_edge_x = self.panel_rect.x
        
        current_surf = self.hide_panel_surf if globals.SHOW_UI_PANEL else self.show_panel_surf
        
        self.toggle_button_rect = current_surf.get_rect(
            centery=self.screen.get_height() // 2,
            right=panel_edge_x - 10
        )
        
        self.screen.blit(current_surf, self.toggle_button_rect)

    def _draw_all_controls_to_surface(self, surface):
        """
        Apenas desenha os controles e textos. O layout já foi calculado.
        """
        #DESENHO TEXTO ESTATICOS
        for surf, pos in self.static_surfaces:
            surface.blit(surf, pos)

        #DESENHO COMPONENTES
        for control in self.controls:
            if isinstance(control, Slider):
                control.draw(surface, self.font_tiny)
            elif isinstance(control, Button):
                control.draw(surface)
        
        #DESENHO TEXTO DINAMICOS
        boid_count_text = self.font_tiny.render(f"Current: {globals.NUM_BIRDS} | Target: {int(self.staged_boid_count)}", True, (200, 200, 200))
        surface.blit(boid_count_text, (self.boid_count_slider.rect.x, self.boid_count_slider.rect.y - 25))
    
    def update(self):
        if globals.SHOW_UI_PANEL:
            self.target_x = self.visible_x
        else:
            self.target_x = self.hidden_x
            
        if abs(self.target_x - self.current_x) > 0.5:
            self.current_x += (self.target_x - self.current_x) * self.animation_speed
        else:
            self.current_x = self.target_x
    
        self.panel_rect.x = int(self.current_x)
        globals.UI_PANEL_RECT = self.panel_rect
    
    def draw(self):
        
        self.draw_fps()
        self._draw_toggle_button()
        if self.current_x < self.screen.get_width():
            self.content_surface.fill((20, 25, 35))
            self._draw_all_controls_to_surface(self.content_surface)

            self.visible_panel.fill((20, 25, 35))
            view_rect = pygame.Rect(0, self.scroll_offset_y, self.panel_width, self.panel_height)
            self.visible_panel.blit(self.content_surface, (0, 0), view_rect)

            self._draw_scrollbar()
            
            self.screen.blit(self.visible_panel, self.panel_rect)