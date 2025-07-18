#ifndef SIMULATION_H
#define SIMULATION_H
#include <stdbool.h>
#include <stdlib.h>
#include <math.h>
#include <omp.h>
#include "datatypes.h"

void update_boids(Boids* boids, Grid *grid, 
    float visual_range, float protected_range,
    float centering_factor, float matching_factor, float avoid_factor,
    float turn_factor, float max_speed, float min_speed,
    int screen_width, int screen_height, int margin, int mouse_x, int mouse_y, bool mouse_motion,
    bool mouse_fear, bool mouse_attraction, int mouse_fear_radius, int mouse_attraction_radius);

#endif
