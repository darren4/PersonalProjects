#include "organisms.h"
#include "random_numbers.h"

#include <cstdlib>


struct InheritedTraits {
    InheritedTraits() {
        strength = random_int(0, 5);
        offspring_capacity = random_int(0, 5);
        calorie_usage = random_int(0, 5);
    }

    InheritedTraits(unsigned int _strength, unsigned int _offspring_capacity, float _calorie_usage): 
        strength(_strength), offspring_capacity(_offspring_capacity), calorie_usage(_calorie_usage) {}

    InheritedTraits(const InheritedTraits& inherited_traits): 
        strength(inherited_traits.strength),
        offspring_capacity(inherited_traits.offspring_capacity),
        calorie_usage(inherited_traits.calorie_usage) {}

    void operator=(const InheritedTraits& inherited_traits) {
        strength = inherited_traits.strength;
        offspring_capacity = inherited_traits.offspring_capacity;
        calorie_usage = inherited_traits.calorie_usage;
    }
};


