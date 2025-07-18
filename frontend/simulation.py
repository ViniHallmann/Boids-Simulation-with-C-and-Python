import globals
import state

class Simulation:
    def __init__(self):
        """
        Inicializa os dados da simulação (boids e grids) na biblioteca C.
        """
        print("P: Inicializando estado da simulação...")

        self.boids = state.boids_lib.initialize_boids(
            globals.NUM_BIRDS, globals.SCREEN_WIDTH, globals.SCREEN_HEIGHT, globals.SpawnMode.SPAWN_TOP_LEFT
        )
        self.grid = state.boids_lib.create_grid(
            globals.SCREEN_WIDTH, globals.SCREEN_HEIGHT, globals.VISUAL_RANGE
        )

        self.update_args = (
            globals.VISUAL_RANGE, globals.PROTECTED_RANGE, globals.CENTERING_FACTOR,
            globals.MATCHING_FACTOR, globals.AVOID_FACTOR, globals.TURN_FACTOR,
            globals.MAX_SPEED, globals.MIN_SPEED, globals.SCREEN_WIDTH,
            globals.SCREEN_HEIGHT, globals.MARGIN
        )

    def update(self):
        """
        Chama a função de atualização da biblioteca C para avançar a simulação.
        """
        state.boids_lib.update_boids(self.boids, self.grid, *self.update_args, *globals.MOUSE_POS)

    def cleanup(self):
        """
        Libera a memória alocada pela biblioteca C.
        """
        print("P: Limpando memória da simulação C...")
        state.boids_lib.free_grid(self.grid)
        state.boids_lib.free_boids(self.boids)