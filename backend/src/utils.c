#include "utils.h"
#include <time.h>
#include <stdlib.h>

void initialize_seed(void) {
    srand(time(NULL));
}