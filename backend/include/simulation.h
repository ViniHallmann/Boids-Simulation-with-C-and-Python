#ifndef SIMULATION_H
#define SIMULATION_H
#include <stdbool.h>
#include <stdlib.h>
#include <math.h>
#include <omp.h>
#include "datatypes.h"

typedef enum {
    BOUNDARY_TURN,   
    BOUNDARY_BOUNCE, 
    BOUNDARY_WRAP    
} BoundaryBehavior;

void update_boids(Boids* boids, Grid *grid, BoundaryBehavior behavior,
    float visual_range, float protected_range,
    float centering_factor, float matching_factor, float avoid_factor,
    float turn_factor, float bounce_factor, 
    float max_speed, float min_speed,
    int screen_width, int screen_height, int margin,
    int mouse_x, int mouse_y, bool mouse_motion,
    bool mouse_fear, bool mouse_attraction,
    int mouse_fear_radius, int mouse_attraction_radius); 


#endif
