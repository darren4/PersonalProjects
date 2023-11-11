#include "organisms.h"
#include "random_numbers.h"
#include "simulation_parameters.h"

#include <cstdlib>
#include <vector>
#include <algorithm>
#include <mutex>

// --- InheritedTraits ---

InheritedTraits::InheritedTraits() {
    strength = random_int(MIN_ORGANISM_STRENGTH, MAX_ORGANISM_STRENGTH);
    offspring_capacity = random_int(MIN_ORGANISM_OFFSPRING_CAPACITY, MAX_ORGANISM_OFFSPRING_CAPACITY);
    calorie_usage = random_int(MIN_ORGANISM_CALORIE_USAGE, MAX_ORGANISM_CALORIE_USAGE);
}

InheritedTraits::InheritedTraits(size_t _strength, size_t _offspring_capacity, size_t _calorie_usage):
    strength(_strength), offspring_capacity(_offspring_capacity), calorie_usage(_calorie_usage) {}

InheritedTraits::InheritedTraits(const InheritedTraits& other):
    strength(other.strength),
    offspring_capacity(other.offspring_capacity),
    calorie_usage(other.calorie_usage) {}

InheritedTraits::InheritedTraits(const InheritedTraits& first, const InheritedTraits& second) {
    strength = (random_int(0, 1)) ? first.strength : second.strength;
    offspring_capacity = (random_int(0, 1)) ? first.offspring_capacity : second.offspring_capacity;
    calorie_usage = (random_int(0, 1)) ? first.calorie_usage : second.calorie_usage;
}

InheritedTraits& InheritedTraits::operator=(const InheritedTraits& other) {
    if (this == &other)
        return *this;

    strength = other.strength;
    offspring_capacity = other.offspring_capacity;
    calorie_usage = other.calorie_usage;

    return *this;
}

InheritedTraits& InheritedTraits::operator+=(const InheritedTraits& other) {
    strength += other.strength;
    offspring_capacity += other.offspring_capacity;
    calorie_usage += other.offspring_capacity;
    return *this;
}

InheritedTraits& InheritedTraits::operator-=(const InheritedTraits& other) {
    strength -= other.strength;
    offspring_capacity -= other.offspring_capacity;
    calorie_usage -= other.offspring_capacity;
    return *this;
}

// --- SpeciesStatus ---

SpeciesStatus::SpeciesStatus() : round(0), filename(""), alive_count(0), created_in_round(0), eaten_in_round(0), starved_in_round(0) {}

void SpeciesStatus::save_to_file() {
    filestream << round << ",";
    filestream << alive_count << ",";
    filestream << created_in_round << ",";
    filestream << eaten_in_round << ",";
    filestream << starved_in_round << ",";
    filestream << inherited_traits_totals.strength / alive_count << ",";
    filestream << inherited_traits_totals.offspring_capacity / alive_count << ",";
    filestream << inherited_traits_totals.calorie_usage / alive_count;
    filestream << "\n";
    ++round;
}

void SpeciesStatus::reset_round() {
    std::unique_lock<std::mutex> status_lock(status_mutex);
    created_in_round = 0;
    eaten_in_round = 0;
    starved_in_round = 0;
}

void SpeciesStatus::set_filename(std::string name) {
    filename = name;
    filestream = std::ofstream(filename);
    filestream << "round,";
    filestream << "alive_count,";
    filestream << "created_in_round,";
    filestream << "eaten_in_round,";
    filestream << "starved_in_round,";
    filestream << "avg_strength,";
    filestream << "avg_offspring_capacity,";
    filestream << "avg_calorie_usage";
    filestream << "\n";
}

bool SpeciesStatus::log_round_and_reset() {
    if (alive_count > 0) {
        save_to_file();
        reset_round();
        return true;
    }
    else {
        return false;
    }
}

void SpeciesStatus::created(const InheritedTraits& organism_traits) {
    std::unique_lock<std::mutex> status_lock(status_mutex);
    inherited_traits_totals += organism_traits;
    ++created_in_round;
    ++alive_count;
}

void SpeciesStatus::eaten(const InheritedTraits& organism_traits) {
    std::unique_lock<std::mutex> status_lock(status_mutex);
    inherited_traits_totals -= organism_traits;
    ++eaten_in_round;
    --alive_count;
}

void SpeciesStatus::starved(const InheritedTraits& organism_traits) {
    std::unique_lock<std::mutex> status_lock(status_mutex);
    inherited_traits_totals -= organism_traits;
    ++starved_in_round;
    --alive_count;
}

// --- Organism ---

SpeciesStatus Organism::status_of_organisms;

void Organism::init_organism_logger() {
    Organism::status_of_organisms.set_filename("organism_status.csv");
}

bool Organism::log_organism_status() {
    return Organism::status_of_organisms.log_round_and_reset();
}

Organism::Organism() : alive(true), calorie_count(ORGANISM_STARTING_CALORIES) {}

Organism::Organism(const InheritedTraits& inherited_traits) : alive(true), calorie_count(10), traits(inherited_traits) {}

const InheritedTraits& Organism::get_traits() const {
    return traits;
}

bool Organism::still_alive() const {
    return alive;
}

// --- Prey ---

SpeciesStatus Prey::status_of_prey;

void Prey::init_prey_logger() {
    Prey::status_of_prey.set_filename("prey_status.csv");
}

bool Prey::log_prey_status() {
    return Prey::status_of_prey.log_round_and_reset();
}

Prey* Prey::get_new() {
    return new Prey();
}

Prey* Prey::get_new_with_traits(const InheritedTraits& inherited_traits) {
    return new Prey(inherited_traits);
}

Prey::Prey() {
    Prey::status_of_prey.created(traits);
    Organism::status_of_organisms.created(traits);
}
Prey::Prey(const InheritedTraits& inherited_traits) : Organism(inherited_traits) {
    Prey::status_of_prey.created(traits);
    Organism::status_of_organisms.created(traits);
}

void Prey::eat_for_day(size_t food_amount) {
    if (alive) {
        calorie_count += (food_amount - traits.calorie_usage);
        if (calorie_count <= 0) {
            alive = false;
            Prey::status_of_prey.starved(traits);
            Organism::status_of_organisms.starved(traits);
        }
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
    Prey::status_of_prey.eaten(traits);
    Organism::status_of_organisms.eaten(traits);
}

// --- Predator ---

SpeciesStatus Predator::status_of_predators;

void Predator::init_predator_logger() {
    Predator::status_of_predators.set_filename("predators_status.csv");
}

bool Predator::log_predator_status() {
    return Predator::status_of_predators.log_round_and_reset();
}

Predator* Predator::get_new() {
    return new Predator();
}

Predator* Predator::get_new_with_traits(const InheritedTraits& inherited_traits) {
    return new Predator(inherited_traits);
}

Predator::Predator() {
    Predator::status_of_predators.created(traits);
    Organism::status_of_organisms.created(traits);
}

Predator::Predator(const InheritedTraits& inherited_traits) : Organism(inherited_traits) {
    Predator::status_of_predators.created(traits);
    Organism::status_of_organisms.created(traits);
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
        Predator::status_of_predators.starved(traits);
        Organism::status_of_organisms.starved(traits);
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
