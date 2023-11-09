#include "random_numbers.h"
#include <cstdlib>
#include <assert.h> 


size_t random_int(size_t start, size_t end){
    assert(start <= end);
    if (start == end) {
        return start;
    }
    else {
        size_t diff = end - start;
        return start + (rand() % diff);
    }
}
