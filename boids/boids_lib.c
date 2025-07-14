#include <stdio.h>
#include <stdlib.h>
#include <time.h>

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

Boids* initialize_boids(int count) {
    Boids *boids = create_boids(count);
    if (!boids) return NULL;

    for (int i = 0; i < count; i++) {
        boids->entities[i].position.x = (float)(rand() % 100);
        boids->entities[i].position.y = (float)(rand() % 100);
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

void update_boids(Boids* boids) {
    if (!boids) return;

     for (int i = 0; i < boids->count; i++) {
         boids->entities[i].position.x += boids->entities[i].velocity.vx;
         boids->entities[i].position.y += boids->entities[i].velocity.vy;
    }

    printf("C: Posição atual do Boid 0: (%.2f, %.2f)\n",
           boids->entities[0].position.x,
           boids->entities[0].position.y);
}