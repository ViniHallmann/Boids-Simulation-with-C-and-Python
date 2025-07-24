import pygame
import globals
import state


class Simulation:
    def __init__(self, num_birds: int = globals.NUM_BIRDS):
        """
        Inicializa os dados da simulação (boids e grids) na biblioteca C.
        """
        print("P: Inicializando estado da simulação...")

        self.boids = state.boids_lib.initialize_boids(
            num_birds,
            globals.SCREEN_WIDTH,
            globals.SCREEN_HEIGHT,
            globals.SpawnMode.SPAWN_TOP_LEFT
        )
        self.grid = state.boids_lib.create_grid(
            globals.SCREEN_WIDTH,
            globals.SCREEN_HEIGHT,
            globals.VISUAL_RANGE
        )

    def update(self):
        """
        Chama a função de atualização da biblioteca C para avançar a simulação.
        Só atualiza se não estiver pausada.
        """
        if not globals.PAUSED:
            # --- LÓGICA DE ATIVAÇÃO DO MOUSE ---
            # TA quebrado sla arruma ai
            # mouse_over_ui = False
            # if globals.UI_PANEL_RECT and globals.SHOW_UI_PANEL:
            #     mouse_over_ui = globals.UI_PANEL_RECT.collidepoint(pygame.mouse.get_pos())

            # mouse_is_active = globals.MOUSE_MOTION and pygame.mouse.get_focused() and not mouse_over_ui

            state.boids_lib.update_boids(
                self.boids,                      # 1
                self.grid,                       # 2
                globals.BOUNDARY_BEHAVIOR.value, # 3
                globals.VISUAL_RANGE,            # 4
                globals.PROTECTED_RANGE,         # 5
                globals.CENTERING_FACTOR,        # 6
                globals.MATCHING_FACTOR,         # 7
                globals.AVOID_FACTOR,            # 8
                globals.TURN_FACTOR,             # 9
                globals.BOUNCE_FACTOR,           # 10
                globals.MAX_SPEED,               # 11
                globals.MIN_SPEED,               # 12
                globals.SCREEN_WIDTH,            # 13
                globals.SCREEN_HEIGHT,           # 14
                globals.MARGIN,                  # 15
                globals.MOUSE_POS[0],            # 16
                globals.MOUSE_POS[1],            # 17
                #mouse_is_active,                 # 18
                globals.MOUSE_MOTION,            # 18
                globals.MOUSE_FEAR,              # 19
                globals.MOUSE_ATTRACTION,        # 20
                globals.MOUSE_FEAR_RADIUS,       # 21
                globals.MOUSE_ATTRACTION_RADIUS  # 22
            )

    def cleanup(self):
        """
        Libera a memória alocada pela biblioteca C.
        """
        print("P: Limpando memória da simulação C...")
        state.boids_lib.free_grid(self.grid)
        state.boids_lib.free_boids(self.boids)