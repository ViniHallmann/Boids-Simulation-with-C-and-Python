#include "simulation.h"
#include "grid.h" 
#include <stdlib.h>
#include <math.h>
#include <omp.h>

static void apply_flocking_rules(Boids* boids, Grid* grid, Velocity* new_velocities, float visual_range_sq, float protected_range_sq, float centering_factor, float matching_factor, float avoid_factor) {
    #pragma omp parallel for
    for (int i = 0; i < boids->count; i++) {
        Entity* boid_i = &boids->entities[i];
        float xpos_avg = 0, ypos_avg = 0, xvel_avg = 0, yvel_avg = 0;
        float close_dx = 0, close_dy = 0;
        int neighboring_boids = 0;

        int boid_cell_x = (int)(boid_i->position.x / grid->cell_size);
        int boid_cell_y = (int)(boid_i->position.y / grid->cell_size);
        
        for (int y = boid_cell_y - 1; y <= boid_cell_y + 1; y++) {
            for (int x = boid_cell_x - 1; x <= boid_cell_x + 1; x++) {
                if (x < 0 || x >= grid->cols || y < 0 || y >= grid->rows) continue;

                int cell_index = y * grid->cols + x;
                BoidNode* node = grid->cells[cell_index];

                while (node != NULL) {
                    Entity* boid_j = node->boid_entity;
                    if (boid_i == boid_j) {
                        node = node->next;
                        continue;
                    }

                    float dx = boid_i->position.x - boid_j->position.x;
                    float dy = boid_i->position.y - boid_j->position.y;
                    float squared_distance = dx * dx + dy * dy;

                    if (squared_distance < protected_range_sq) {
                        close_dx += dx;
                        close_dy += dy;
                    } else if (squared_distance < visual_range_sq) {
                        xpos_avg += boid_j->position.x;
                        ypos_avg += boid_j->position.y;
                        xvel_avg += boid_j->velocity.vx;
                        yvel_avg += boid_j->velocity.vy;
                        neighboring_boids++;
                    }
                    node = node->next;
                }
            }
        }

        Velocity final_velocity = boid_i->velocity;
        if (neighboring_boids > 0) {
            xpos_avg /= neighboring_boids; ypos_avg /= neighboring_boids;
            xvel_avg /= neighboring_boids; yvel_avg /= neighboring_boids;

            final_velocity.vx += (xpos_avg - boid_i->position.x) * centering_factor;
            final_velocity.vy += (ypos_avg - boid_i->position.y) * centering_factor;
            final_velocity.vx += (xvel_avg - boid_i->velocity.vx) * matching_factor;
            final_velocity.vy += (yvel_avg - boid_i->velocity.vy) * matching_factor;
        }

        final_velocity.vx += close_dx * avoid_factor;
        final_velocity.vy += close_dy * avoid_factor;
        new_velocities[i] = final_velocity;
    }
}

static void enforce_speed_limits(Entity* boid, float max_speed, float min_speed) {
    float speed = sqrtf(boid->velocity.vx * boid->velocity.vx + boid->velocity.vy * boid->velocity.vy);
    if (speed == 0) return;
    if (speed > max_speed) {
        boid->velocity.vx = (boid->velocity.vx / speed) * max_speed;
        boid->velocity.vy = (boid->velocity.vy / speed) * max_speed;
    } else if (speed < min_speed) {
        boid->velocity.vx = (boid->velocity.vx / speed) * min_speed;
        boid->velocity.vy = (boid->velocity.vy / speed) * min_speed;
    }
}

static void enforce_screen_boundaries(Entity* boid, float turn_factor, int width, int height, int margin) {
    if (boid->position.x < margin) boid->velocity.vx += turn_factor;
    if (boid->position.x > width - margin) boid->velocity.vx -= turn_factor;
    if (boid->position.y < margin) boid->velocity.vy += turn_factor;
    if (boid->position.y > height - margin) boid->velocity.vy -= turn_factor;
}

void update_boids(Boids* boids, Grid *grid, float visual_range, float protected_range, float centering_factor, float matching_factor, float avoid_factor,float turn_factor, float max_speed, float min_speed, int screen_width, int screen_height, int margin) {
    if (!boids || boids->count == 0) return;

    Velocity* new_velocities = (Velocity*) malloc(boids->count * sizeof(Velocity));
    if (!new_velocities) return;

    float visual_range_sq = visual_range * visual_range;
    float protected_range_sq = protected_range * protected_range;

    clear_grid(grid);
    for (int i = 0; i < boids->count; i++) {
        add_to_grid(grid, &boids->entities[i]);
    }

    apply_flocking_rules(boids, grid, new_velocities, visual_range_sq, protected_range_sq, centering_factor, matching_factor, avoid_factor);

    #pragma omp parallel for
    for (int i = 0; i < boids->count; i++) {
        Entity* boid = &boids->entities[i];
        boid->velocity = new_velocities[i];

        enforce_screen_boundaries(boid, turn_factor, screen_width, screen_height, margin);
        enforce_speed_limits(boid, max_speed, min_speed);

        boid->position.x += boid->velocity.vx;
        boid->position.y += boid->velocity.vy;
    }
    free(new_velocities);
}