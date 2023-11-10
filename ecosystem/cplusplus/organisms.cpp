#include "organisms.h"
#include "random_numbers.h"
#include "simulation_parameters.h"

#include <cstdlib>
#include <vector>
#include <algorithm>

// --- InheritedTraits ---

InheritedTraits::InheritedTraits() {
    strength = random_int(MIN_ORGANISM_STRENGTH, MAX_ORGANISM_STRENGTH);
    offspring_capacity = random_int(MIN_ORGANISM_OFFSPRING_CAPACITY, MAX_ORGANISM_OFFSPRING_CAPACITY);
    calorie_usage = random_int(MIN_ORGANISM_CALORIE_USAGE, MAX_ORGANISM_CALORIE_USAGE);
}

InheritedTraits::InheritedTraits(size_t _strength, size_t _offspring_capacity, size_t _calorie_usage):
    strength(_strength), offspring_capacity(_offspring_capacity), calorie_usage(_calorie_usage) {}

InheritedTraits::InheritedTraits(const InheritedTraits& inherited_traits):
    strength(inherited_traits.strength),
    offspring_capacity(inherited_traits.offspring_capacity),
    calorie_usage(inherited_traits.calorie_usage) {}

InheritedTraits::InheritedTraits(const InheritedTraits& first, const InheritedTraits& second) {
    strength = (random_int(0, 1)) ? first.strength : second.strength;
    offspring_capacity = (random_int(0, 1)) ? first.offspring_capacity : second.offspring_capacity;
    calorie_usage = (random_int(0, 1)) ? first.calorie_usage : second.calorie_usage;
}

InheritedTraits& InheritedTraits::operator=(const InheritedTraits& inherited_traits) {
    if (this == &inherited_traits)
        return *this;

    strength = inherited_traits.strength;
    offspring_capacity = inherited_traits.offspring_capacity;
    calorie_usage = inherited_traits.calorie_usage;

    return *this;
}

// --- SpeciesStatus ---

SpeciesStatus::SpeciesStatus() : alive_count(0), created_in_round(0), eaten_in_round(0), starved_in_round(0) {}

void SpeciesStatus::reset_round() {
    created_in_round = 0;
    eaten_in_round = 0;
    starved_in_round = 0;
}

// --- Organism ---

Organism::Organism() : alive(true), calorie_count(10) {}

Organism::Organism(const InheritedTraits& inherited_traits) : alive(true), calorie_count(10), traits(inherited_traits) {}

const InheritedTraits& Organism::get_traits() const {
    return traits;
}

bool Organism::still_alive() const {
    return alive;
}

// --- Prey ---

Prey* Prey::get_new() {
    return new Prey();
}

Prey* Prey::get_new_with_traits(const InheritedTraits& inherited_traits) {
    return new Prey(inherited_traits);
}

Prey::Prey() {}
Prey::Prey(const InheritedTraits& inherited_traits) : Organism(inherited_traits) {}

void Prey::eat_for_day(size_t food_amount) {
    if (alive) {
        calorie_count += (food_amount - traits.calorie_usage);
        alive = calorie_count > 0;
    }
}

void Prey::reproduce(Prey* mate, std::vector<Prey*> prey) {
    size_t new_offspring_count = std::min(traits.calorie_usage, mate->get_traits().calorie_usage);
    for (size_t i = 0; i < new_offspring_count; ++i) {
        InheritedTraits new_traits(traits, mate->get_traits());
        Prey* new_prey = Prey::get_new_with_traits(new_traits);
        prey.push_back(new_prey);
    }
}

size_t Prey::get_strength() const {
    return traits.strength;
}

size_t Prey::get_calorie_count() const {
    return calorie_count;
}

void Prey::eaten() {
    alive = false;
}

// --- Predator ---

Predator* Predator::get_new() {
    return new Predator();
}

Predator* Predator::get_new_with_traits(const InheritedTraits& inherited_traits) {
    return new Predator(inherited_traits);
}

Predator::Predator() {}

Predator::Predator(const InheritedTraits& inherited_traits) : Organism(inherited_traits) {}

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

void Predator::reproduce(Predator* mate, std::vector<Predator*> predators) {
    size_t new_offspring_count = std::min(traits.calorie_usage, mate->get_traits().calorie_usage);
    for (size_t i = 0; i < new_offspring_count; ++i) {
        InheritedTraits new_traits(traits, mate->get_traits());
        Predator* new_predator = Predator::get_new_with_traits(new_traits);
        predators.push_back(new_predator);
    }
}
