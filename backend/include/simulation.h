#ifndef SIMULATION_H
#define SIMULATION_H

#include "datatypes.h"

void update_boids(Boids* boids, Grid *grid, 
    float visual_range, float protected_range,
    float centering_factor, float matching_factor, float avoid_factor,
    float turn_factor, float max_speed, float min_speed,
    int screen_width, int screen_height, int margin);

#endif