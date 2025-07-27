import pygame
import globals
import time
import json
import os

# --- COMPONENTES DA UI REUTILIZÁVEIS ---

class Slider:
    def __init__(self, label, min_val, max_val, initial_val, callback, value_factor=1.0, step=None):
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.callback = callback
        self.value_factor = value_factor
        self.step = step
        self.dragging = False
        self.rect = None
        self.handle_radius = 0
        self.font_surface = None

    def layout(self, x, y, width, height, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.handle_radius = height // 2
        label_text = f"{self.label}:"
        self.font_surface = font.render(label_text, True, (200, 200, 200))

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
        surface.blit(self.font_surface, (self.rect.x, self.rect.y - 18))
        display_val = self.val * self.value_factor
        value_text = f"{display_val:.3f}" if isinstance(display_val, float) and self.step is None else f"{int(display_val)}"
        value_surface = font.render(value_text, True, (255, 255, 255))
        surface.blit(value_surface, (self.rect.right - value_surface.get_width(), self.rect.y - 18))       
        pygame.draw.rect(surface, (60, 60, 60), self.rect, border_radius=self.rect.height // 2)

        if self.max_val > self.min_val:
            handle_x = self.rect.x + (self.val - self.min_val) / (self.max_val - self.min_val) * self.rect.width
            pygame.draw.circle(surface, (100, 150, 255), (int(handle_x), self.rect.centery), self.handle_radius + 1)
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
        self.font_surface = None

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
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, (100, 100, 100), self.rect, width=1, border_radius=5)
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
        
        self.font_large = pygame.font.Font(None, 32)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        self.font_tiny = pygame.font.Font(None, 16)

        self.last_fps_text = ""
        self.fps_surface = None

        self.panel_width = 320
        self.panel_height = screen.get_height()

        self.visible_x = self.screen.get_width() - self.panel_width
        self.hidden_x = self.screen.get_width()
        self.target_x = self.hidden_x
        self.current_x = float(self.hidden_x)

        self.animation_speed = 0.1 

        self.visible_panel = pygame.Surface((self.panel_width, self.panel_height))
        self.visible_panel.set_alpha(230)
        self.panel_rect = self.visible_panel.get_rect(topleft=(self.current_x, 0))
        globals.UI_PANEL_RECT = self.panel_rect

        self.content_surface = None
        self.content_height = 0
        self.scroll_offset_y = 0
        self.scroll_speed = 40

        self.staged_boid_count = globals.NUM_BIRDS
        
        self.settings_dir = "settings"
        self.settings_filepath = os.path.join(self.settings_dir, "settings.json")

        self.init_controls()
        print("P: UI inicializada com sucesso (versão com Import/Export).")

    # Corrigido: Slider do min_speed não pode ficar acima do max_speed
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
            self.min_speed_slider, # Adiciona o slider de min speed à lista
            self.max_speed_slider  # Adiciona o slider de max speed à lista
        ]
        self.controls.extend(self.sliders)
        
        self.display_sliders = [
            Slider("Visual Range", 10.0, 200.0, globals.DEFAULT_SETTINGS["VISUAL_RANGE"], lambda v: setattr(globals, 'VISUAL_RANGE', v), step=1),
            Slider("Protected Range", 5.0, 100.0, globals.DEFAULT_SETTINGS["PROTECTED_RANGE"], lambda v: setattr(globals, 'PROTECTED_RANGE', v), step=1),
        ]
        self.controls.extend(self.display_sliders)
        
        self.toggles = [
            ToggleButton("Mouse Influence", globals.MOUSE_MOTION, lambda s: setattr(globals, 'MOUSE_MOTION', s)),
            ToggleButton("Show Margin", globals.MARGIN_LINE, lambda s: setattr(globals, 'MARGIN_LINE', s)),
            ToggleButton("Show Visual Range", globals.DRAW_VISUAL_RANGE, lambda s: setattr(globals, 'DRAW_VISUAL_RANGE', s)),
            ToggleButton("Show Protected Range", globals.DRAW_PROTECTED_RANGE, lambda s: setattr(globals, 'DRAW_PROTECTED_RANGE', s)),
        ]
        self.controls.extend(self.toggles)

        self.boid_count_slider = Slider("Boids Count", 10, 5000, self.staged_boid_count, lambda v: setattr(self, 'staged_boid_count', v), step=10)
        self.controls.append(self.boid_count_slider)
        
        self.apply_boids_button = Button("Apply Count & Restart", self.post_restart_event, color=(60, 100, 140))
        self.controls.append(self.apply_boids_button)

        self.behavior_buttons = [
            Button("Turn", lambda: setattr(globals, 'BOUNDARY_BEHAVIOR', globals.BoundaryBehavior.BOUNDARY_TURN)),
            Button("Bounce", lambda: setattr(globals, 'BOUNDARY_BEHAVIOR', globals.BoundaryBehavior.BOUNDARY_BOUNCE)),
            Button("Wrap", lambda: setattr(globals, 'BOUNDARY_BEHAVIOR', globals.BoundaryBehavior.BOUNDARY_WRAP))
        ]
        self.controls.extend(self.behavior_buttons)

        self.main_buttons = [
            Button("Pause", self.toggle_pause, color=(120, 50, 50)),
            Button("Reset to Defaults", self.reset_to_defaults, color=(120, 80, 60)),
            Button("Export Settings", self._export_settings, color=(80, 120, 60)),
            Button("Import Settings", self._import_settings, color=(120, 80, 80)),
            Button("Restart Simulation", self.post_restart_event, color=(60, 80, 120))
        ]
        self.controls.extend(self.main_buttons)
        self.pause_button = self.main_buttons[0]
        self.update_pause_button_state()
        
        temp_surface = pygame.Surface((self.panel_width, 1)) 
        self.content_height = self._draw_all_controls_to_surface(temp_surface)
        self.content_surface = pygame.Surface((self.panel_width, self.content_height))

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
                    "Mouse Influence": "MOUSE_MOTION",
                    "Show Margin": "MARGIN_LINE", "Show Visual Range": "DRAW_VISUAL_RANGE", "Show Protected Range": "DRAW_PROTECTED_RANGE"
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

    def handle_event(self, event):
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
            self.pause_button.label = "▶ Play"
            self.pause_button.color = (50, 120, 50)
        else:
            self.pause_button.label = "❚❚ Pause"
            self.pause_button.color = (120, 50, 50)
        self.pause_button.hover_color = tuple(min(c + 25, 255) for c in self.pause_button.color)
        self.pause_button.font_surface = self.font_medium.render(self.pause_button.label, True, (255, 255, 255))
        
    def draw_fps(self):
        current_fps_text = f"FPS: {self.clock.get_fps():.0f}"
        if current_fps_text != self.last_fps_text:
            self.last_fps_text = current_fps_text
            self.fps_surface = self.font_medium.render(current_fps_text, True, (255, 255, 255))
        if self.fps_surface:
            self.screen.blit(self.fps_surface, (10, 10))

    def draw(self):
        self.draw_fps()
        if self.current_x < self.screen.get_width():
            self.content_surface.fill((20, 25, 35))
            self._draw_all_controls_to_surface(self.content_surface)

            self.visible_panel.fill((20, 25, 35))
            view_rect = pygame.Rect(0, self.scroll_offset_y, self.panel_width, self.panel_height)
            self.visible_panel.blit(self.content_surface, (0, 0), view_rect)

            self._draw_scrollbar()
            
            self.screen.blit(self.visible_panel, self.panel_rect)

    def _draw_all_controls_to_surface(self, surface):
        x_margin = 20
        scrollbar_gutter = 20
        content_width = self.panel_width - x_margin - scrollbar_gutter
        y_cursor = 20
        
        title_surf = self.font_large.render("Boids Simulation Controls", True, (100, 150, 255))
        surface.blit(title_surf, (x_margin, y_cursor))
        y_cursor += 50

        instructions = [
            "Move the mouse around or just watch them flock.",
            "Left-click to toggle fear mode on/off.",
            "Press Spacebar or the Pause button to pause."
        ]
        
        for line in instructions:
            instruction_surf = self.font_small.render(line, True, (180, 180, 180))
            surface.blit(instruction_surf, (x_margin, y_cursor))
            y_cursor += 20 
        y_cursor += 20

        button_width = (content_width) / 2 - 5
        self.main_buttons[0].layout(x_margin, y_cursor, button_width, 30, self.font_medium)
        self.main_buttons[1].layout(x_margin + button_width + 10, y_cursor, button_width, 30, self.font_medium)
        y_cursor += 40
        self.main_buttons[2].layout(x_margin, y_cursor, button_width, 30, self.font_medium)
        self.main_buttons[3].layout(x_margin + button_width + 10, y_cursor, button_width, 30, self.font_medium)
        y_cursor += 45
        self.main_buttons[4].layout(x_margin, y_cursor, content_width, 35, self.font_medium)
        y_cursor += 50

        for btn in self.main_buttons:
            btn.draw(surface)
        
        def draw_section(title, controls, start_y, spacing, font, layout_func=None):
            start_y += 15
            header_surf = font.render(title, True, (220, 220, 220))
            surface.blit(header_surf, (x_margin, start_y))
            y = start_y + 40
            for control in controls:
                if layout_func:
                    layout_func(control, y)
                control.draw(surface, self.font_tiny)
                y += spacing
            return y
        
        slider_layout = lambda ctrl, y: ctrl.layout(x_margin, y, content_width, 15, self.font_tiny)
        y_cursor = draw_section("Behavior", self.sliders, y_cursor, 45, self.font_medium, slider_layout)
        y_cursor = draw_section("Display", self.display_sliders, y_cursor, 45, self.font_medium, slider_layout)
        
        y_cursor += 15
        header_surf = self.font_medium.render("Boundary Behavior", True, (220, 220, 220))
        surface.blit(header_surf, (x_margin, y_cursor))
        y_cursor += 40
        
        button_width_bh = (content_width) / 3 - 8
        for i, btn in enumerate(self.behavior_buttons):
            is_active = globals.BOUNDARY_BEHAVIOR.name.endswith(btn.label.upper())
            original_color = (60, 140, 180) if is_active else (70, 70, 70)
            
            btn.color = original_color
            btn.hover_color = tuple(min(c + 25, 255) for c in btn.color)

            btn.layout(x_margin + i * (button_width_bh + 10), y_cursor, button_width_bh, 30, self.font_small)
            btn.draw(surface)
        y_cursor += 45

        y_cursor += 15
        header_surf = self.font_medium.render("Debug Toggles", True, (220, 220, 220))
        surface.blit(header_surf, (x_margin, y_cursor))
        toggle_y = y_cursor + 40
        
        toggle_width = (content_width - 10) / 2
        for i, toggle in enumerate(self.toggles):
            row = i // 2
            col = i % 2
            x_pos = x_margin + col * (toggle_width + 10)
            y_pos = toggle_y + row * 40
            toggle.layout(x_pos, y_pos, toggle_width, 30, self.font_small)
            toggle.draw(surface)
        
        num_toggle_rows = (len(self.toggles) + 1) // 2
        y_cursor = toggle_y + num_toggle_rows * 40

        y_cursor = draw_section("Population", [], y_cursor, 0, self.font_medium)
        
        boid_count_text = self.font_tiny.render(f"Current: {globals.NUM_BIRDS} | Target: {int(self.staged_boid_count)}", True, (200, 200, 200))
        surface.blit(boid_count_text, (x_margin, y_cursor))
        y_cursor += 45
        
        self.boid_count_slider.layout(x_margin, y_cursor, content_width, 20, self.font_tiny)
        self.boid_count_slider.draw(surface, self.font_tiny)
        y_cursor += 35

        self.apply_boids_button.layout(x_margin, y_cursor, content_width, 35, self.font_medium)
        self.apply_boids_button.draw(surface)
        y_cursor += 50
        
        return y_cursor
    
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