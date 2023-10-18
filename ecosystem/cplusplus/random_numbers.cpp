#include "random_numbers.h"
#include <cstdlib>
#include <assert.h> 


float random_float(float start, float end){
    return start + static_cast <float> (rand()) /( static_cast <float> (RAND_MAX/(end-start)));
}


unsigned int random_int(unsigned int start, unsigned int end){
    assert(start <= end);
    unsigned int diff = end - start;
    return start + (rand() % diff);
}
