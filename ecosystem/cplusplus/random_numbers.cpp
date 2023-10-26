#include "random_numbers.h"
#include <cstdlib>
#include <assert.h> 


float random_float(float start, float end){
    return start + static_cast <float> (rand()) /( static_cast <float> (RAND_MAX/(end-start)));
}


size_t random_int(size_t start, size_t end){
    assert(start <= end);
    size_t diff = end - start;
    return start + (rand() % diff);
}
