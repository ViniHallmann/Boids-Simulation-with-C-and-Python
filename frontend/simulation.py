import globals
import state

class Simulation:
    def __init__(self):
        """
        Inicializa os dados da simulação (boids e grids) na biblioteca C.
        """
        print("P: Inicializando estado da simulação...")

        self.boids1 = state.boids_lib.initialize_boids(
            globals.NUM_BIRDS, globals.SCREEN_WIDTH, globals.SCREEN_HEIGHT, 0 # ARRUMAR AQUI ESSA VARIAVEL DE MODE
        )
        self.grid1 = state.boids_lib.create_grid(
            globals.SCREEN_WIDTH, globals.SCREEN_HEIGHT, globals.VISUAL_RANGE
        )

        # self.boids2 = state.boids_lib.initialize_boids(
        #     globals.NUM_BIRDS, globals.SCREEN_WIDTH, globals.SCREEN_HEIGHT, 1
        # )
        # self.grid2 = state.boids_lib.create_grid(
        #     globals.SCREEN_WIDTH, globals.SCREEN_HEIGHT, globals.VISUAL_RANGE
        # )
        
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
        state.boids_lib.update_boids(self.boids1, self.grid1, *self.update_args)
        # state.boids_lib.update_boids(self.boids2, self.grid2, *self.update_args)

    def cleanup(self):
        """
        Libera a memória alocada pela biblioteca C.
        """
        print("P: Limpando memória da simulação C...")
        state.boids_lib.free_grid(self.grid1)
        state.boids_lib.free_boids(self.boids1)
        # state.boids_lib.free_grid(self.grid2)
        # state.boids_lib.free_boids(self.boids2)