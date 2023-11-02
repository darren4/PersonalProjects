#include "organisms.h"
#include "random_numbers.h"

#include <cstdlib>


InheritedTraits::InheritedTraits() {
    // TODO: move this out
    strength = random_int(0, 5);
    offspring_capacity = random_int(0, 5);
    calorie_usage = random_int(0, 5);
}

InheritedTraits::InheritedTraits(size_t _strength, size_t _offspring_capacity, float _calorie_usage):
    strength(_strength), offspring_capacity(_offspring_capacity), calorie_usage(_calorie_usage) {}

InheritedTraits::InheritedTraits(const InheritedTraits& inherited_traits):
    strength(inherited_traits.strength),
    offspring_capacity(inherited_traits.offspring_capacity),
    calorie_usage(inherited_traits.calorie_usage) {}

InheritedTraits InheritedTraits::operator=(const InheritedTraits& inherited_traits) {
    strength = inherited_traits.strength;
    offspring_capacity = inherited_traits.offspring_capacity;
    calorie_usage = inherited_traits.calorie_usage;
}

SpeciesStatus::SpeciesStatus() : alive_count(0), created_in_round(0), eaten_in_round(0), starved_in_round(0) {}

Predator* Predator::new_predator() {
    // TODO: implement
    return nullptr;
}

void Predator::eat_for_day(std::vector<Prey*> prey) {
    calorie_count -= traits.calorie_usage;
    for (Prey* one_prey : prey) {
        if (traits.strength > one_prey->get_strength()) {
            one_prey->eaten();
            calorie_count += one_prey->get_calorie_count();
        }
    }
    if (calorie_count <= 0) {
        alive = false;
    }
}
