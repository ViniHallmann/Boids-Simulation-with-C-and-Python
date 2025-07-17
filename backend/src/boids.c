#include "boids.h"
#include <stdlib.h>
#include <stdio.h>
#include <math.h>

Boids* create_boids(int count) {
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

// int mode eh gambiarra. Transformar em ENUM e tratar com SWITCH!
Boids* initialize_boids(int count, int screen_width, int screen_height, int mode) {
    Boids *boids = create_boids(count);
    if (!boids) return NULL;

    for (int i = 0; i < count; i++) {
        if (mode == 0) {
            boids->entities[i].position.x = (float)(rand() % 100);
            boids->entities[i].position.y = (float)(rand() % 100);
            boids->entities[i].velocity.vx = (float)(rand() % 10 - 5);
            boids->entities[i].velocity.vy = (float)(rand() % 10 - 5);
        } else {
            boids->entities[i].position.x = (float)(screen_width - 100 + (rand() % 100));
            boids->entities[i].position.y = (float)(screen_height - 100 + (rand() % 100));
            boids->entities[i].velocity.vx = (float)(rand() % 10 - 5);
            boids->entities[i].velocity.vy = (float)(rand() % 10 - 5);
        }
        /* NASCER NO MEIO EM UM QUADRADO DE 50x50

        boids->entities[i].position.x = center_x - 25 + (rand() % 50);
        boids->entities[i].position.y = center_y - 25 + (rand() % 50);

        */


        /* NASCER RANDOMICO NA TELA

            boids->entities[i].position.x = (float)(rand() % screen_width);
            boids->entities[i].position.y = (float)(rand() % screen_height);
            boids->entities[i].velocity.vx = (float)(rand() % 10 - 5);
            boids->entities[i].velocity.vy = (float)(rand() % 10 - 5);

        */


        /* NASCER EM UM CIRCULO

            float angle = ((float)rand() / RAND_MAX) * 2.0f * M_PI;
            float radius = ((float)rand() / RAND_MAX) * spawn_radius;
            boids->entities[i].position.x = center_x + radius * cosf(angle);
            boids->entities[i].position.y = center_y + radius * sinf(angle);
            boids->entities[i].velocity.vx = cosf(angle) * 2.0f;
            boids->entities[i].velocity.vy = sinf(angle) * 2.0f;

        */


        /* NASCER EM CIMA COM VELOCIDADE PARA BAIXO

            boids->entities[i].position.x = (float)(rand() % screen_width);
            boids->entities[i].position.y = (float)(rand() % 50); // Nascem numa faixa de 50px no topo
            boids->entities[i].velocity.vx = ((float)(rand() % 200 - 100) / 100.0f); // -1.0 a 1.0
            boids->entities[i].velocity.vy = 2.0f + ((float)rand() / RAND_MAX);

        */

        /* 50% DE UM LADO 50% DO OUTRO

        if (i < count / 2) {

            boids->entities[i].position.x = (float)(rand() % 100);
            boids->entities[i].position.y = (float)(rand() % screen_height);
            boids->entities[i].velocity.vx = 2.0f + ((float)rand() / RAND_MAX);
            boids->entities[i].velocity.vy = ((float)(rand() % 200 - 100) / 100.0f);

        }

        else {

            boids->entities[i].position.x = (float)(screen_width - 100 + (rand() % 100));
            boids->entities[i].position.y = (float)(rand() % screen_height);
            boids->entities[i].velocity.vx = -2.0f - ((float)rand() / RAND_MAX);
            boids->entities[i].velocity.vy = ((float)(rand() % 200 - 100) / 100.0f);

        }

        */
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