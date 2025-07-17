#ifndef BOIDS_H
#define BOIDS_H

#include "datatypes.h"

Boids* create_boids(int count);
Boids* initialize_boids(int count, int screen_width, int screen_height, int mode);
void free_boids(Boids* boids);

#endif