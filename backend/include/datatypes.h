#ifndef DATATYPES_H
#define DATATYPES_H

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

#endif