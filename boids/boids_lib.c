#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <omp.h> 

/* TO-DO LIST
    * 0. CRIAR MAKEFILE PARA COMPILAR TUDO NUMA TACADA SO
    * 1. Implementar a lógica de atualização dos boids.
    * 2. Adicionar rcoesao alinhamento e separação.
*/

// PARA COMPILAR C: gcc -shared -o libboids.so -fPIC boids_lib.c
typedef struct {
    float x, y;
} Position;

typedef struct {
    float vx, vy;
} Velocity;

typedef struct {
    Position position;
    Velocity velocity;
} Entity;

typedef struct {
    Entity *entities;
    int count;
} Boids;

typedef struct BoidNode {
    Entity* boid_entity;
    struct BoidNode* next;
} BoidNode;

typedef struct {
    int rows;
    int cols;
    float cell_size;
    BoidNode** cells;
} Grid;

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
    int num_cells = grid->cols * grid->rows;
    for (int i = 0; i < num_cells; i++) {
        BoidNode* current = grid->cells[i];
        while (current != NULL) {
            BoidNode* temp = current;
            current = current->next;
            free(temp);
        }
        grid->cells[i] = NULL;
    }
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

    BoidNode* new_node = (BoidNode*) malloc(sizeof(BoidNode));
    if (!new_node) return;

    new_node->boid_entity = boid;
    new_node->next = grid->cells[cell_index]; 
    grid->cells[cell_index] = new_node;
}

Boids* create_boids(int count) {
    srand(time(NULL));

    Boids *boids = (Boids*) malloc(sizeof(Boids));
    if (!boids) return NULL; 

    boids->count = count;
    boids->entities = (Entity*) malloc(count * sizeof(Entity));

    if (!boids->entities) { 
        free(boids);
        return NULL;
    }

    printf("C: Enxame com %d boids criado na memória.\n", count);
    return boids;
}

Boids* initialize_boids(int count, int screen_width, int screen_height) {
    Boids *boids = create_boids(count);
    if (!boids) return NULL;

    float center_x = screen_width / 2.0f;
    float center_y = screen_height / 2.0f;

    for (int i = 0; i < count; i++) {
        boids->entities[i].position.x = center_x - 25 + (rand() % 50);
        boids->entities[i].position.y = center_y - 25 + (rand() % 50);
        
        boids->entities[i].velocity.vx = (float)(rand() % 10 - 5);
        boids->entities[i].velocity.vy = (float)(rand() % 10 - 5);
    }
    return boids;
}

void free_boids(Boids* boids) {
    if (boids) {
        free(boids->entities); 
        free(boids);           
        printf("C: Memória do enxame liberada.\n");
    }
}

static void apply_flocking_rules(Boids* boids, Grid* grid, Velocity* new_velocities, float visual_range_sq, float protected_range_sq, float centering_factor, float matching_factor, float avoid_factor) {
    #pragma omp parallel for
    for (int i = 0; i < boids->count; i++) {
        // Entity* boid_i = &boids->entities[i];
        // float xpos_avg = 0, ypos_avg = 0, xvel_avg = 0, yvel_avg = 0;
        // float close_dx = 0, close_dy = 0;
        // int neighboring_boids = 0;

        // for (int j = 0; j < boids->count; j++) {
        //     if (i == j) continue;
        //     Entity* boid_j = &boids->entities[j];
        //     float dx = boid_i->position.x - boid_j->position.x;
        //     float dy = boid_i->position.y - boid_j->position.y;
        //     float squared_distance = dx * dx + dy * dy;

        //     if (squared_distance < protected_range_sq) {
        //         close_dx += dx;
        //         close_dy += dy;
        //     } else if (squared_distance < visual_range_sq) {
        //         xpos_avg += boid_j->position.x;
        //         ypos_avg += boid_j->position.y;
        //         xvel_avg += boid_j->velocity.vx;
        //         yvel_avg += boid_j->velocity.vy;
        //         neighboring_boids++;
        //     }
        // }

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
    if (speed > max_speed) {
        boid->velocity.vx = (boid->velocity.vx / speed) * max_speed;
        boid->velocity.vy = (boid->velocity.vy / speed) * max_speed;
    } else if (speed < min_speed) {
        boid->velocity.vx = (boid->velocity.vx / speed) * min_speed;
        boid->velocity.vy = (boid->velocity.vy / speed) * min_speed;
    }
}

static void enforce_screen_boundaries(Entity* boid, float turn_factor, int width, int height, int margin) {

    if (boid->position.x < margin) {
        boid->velocity.vx += turn_factor;
    }
    if (boid->position.x > width - margin) {
        boid->velocity.vx -= turn_factor;
    }

    if (boid->position.y < margin) {
        boid->velocity.vy += turn_factor;
    }
    if (boid->position.y > height - margin) {
        boid->velocity.vy -= turn_factor;
    }
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

    //apply_flocking_rules(boids, new_velocities, visual_range_sq, protected_range_sq, centering_factor, matching_factor, avoid_factor);

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