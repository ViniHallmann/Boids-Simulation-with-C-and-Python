#include "grid.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

// Pool de nós para evitar malloc/free constantes
static BoidNode* node_pool = NULL;
static int pool_size = 0;
static int pool_index = 0;

static BoidNode* get_node_from_pool() {
    if (pool_index >= pool_size) {
        // Expandir pool se necessário
        pool_size += 1000;
        node_pool = (BoidNode*) realloc(node_pool, pool_size * sizeof(BoidNode));
    }
    return &node_pool[pool_index++];
}

Grid* create_grid(int screen_width, int screen_height, float cell_size) {
    Grid* grid = (Grid*) malloc(sizeof(Grid));
    if (!grid) return NULL;

    grid->cell_size = cell_size;
    grid->cols = (int)(screen_width / cell_size) + 1;
    grid->rows = (int)(screen_height / cell_size) + 1;

    int num_cells = grid->cols * grid->rows;
    grid->cells = (BoidNode**) calloc(num_cells, sizeof(BoidNode*));
    if (!grid->cells) {
        free(grid);
        return NULL;
    }
    return grid;
}

void clear_grid(Grid* grid) {
    // Reset rápido - apenas zerar ponteiros, manter nós em pool
    int num_cells = grid->cols * grid->rows;
    memset(grid->cells, 0, num_cells * sizeof(BoidNode*));
    pool_index = 0; // Reset do pool para reutilização
}

void free_grid(Grid* grid) {
    if (!grid) return;
    clear_grid(grid);
    free(grid->cells);
    free(grid);
}

void add_to_grid(Grid* grid, Entity* boid) {
    int cell_x = (int)(boid->position.x / grid->cell_size);
    int cell_y = (int)(boid->position.y / grid->cell_size);

    if (cell_x < 0 || cell_x >= grid->cols || cell_y < 0 || cell_y >= grid->rows) return;

    int cell_index = cell_y * grid->cols + cell_x;

    // Usar pool ao invés de malloc
    BoidNode* new_node = get_node_from_pool();
    new_node->boid_entity = boid;
    new_node->next = grid->cells[cell_index];
    grid->cells[cell_index] = new_node;
}