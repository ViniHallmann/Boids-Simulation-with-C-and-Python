#ifndef GRID_H
#define GRID_H

#include "datatypes.h"

Grid* create_grid(int screen_width, int screen_height, float cell_size);
void clear_grid(Grid* grid);
void free_grid(Grid* grid);
void add_to_grid(Grid* grid, Entity* boid);

#endif 