#pragma once

#include "random_numbers.h"

#include <vector>
#include <mutex>
#include <algorithm>



struct InheritedTraits {
    size_t strength;
    size_t offspring_capacity;
    float calorie_usage;

    InheritedTraits();
    InheritedTraits(size_t _strength, size_t _offspring_capacity, float _calorie_usage);
    InheritedTraits(const InheritedTraits& other);
    InheritedTraits(const InheritedTraits& first, const InheritedTraits& second);
    InheritedTraits operator=(const InheritedTraits& other);
};

struct SpeciesStatus {
    size_t alive_count;
    std::mutex alive_count_mutex;

    size_t created_in_round;
    std::mutex created_in_round_mutex;

    size_t eaten_in_round;
    std::mutex eaten_in_round_mutex;

    size_t starved_in_round;
    std::mutex starved_in_round_mutex;

    InheritedTraits inherited_traits_totals;

    SpeciesStatus();
    SpeciesStatus(const SpeciesStatus& other) = delete;
    SpeciesStatus operator=(const SpeciesStatus& other) = delete;

    void reset_round();
};

class Organism {
protected:
    bool alive;
    size_t calorie_count;
    InheritedTraits traits;

public:
    Organism();
    Organism(const Organism& other);
    Organism(const InheritedTraits& inherited_traits);
    Organism operator=(const Organism& other);

    const InheritedTraits& get_traits();
    bool still_alive();
};

class Prey : public Organism {
private:
    static SpeciesStatus species_status;

public:
    static Prey* get_new();
    static Prey* get_new_with_traits(const InheritedTraits& inherited_traits);

    Prey();
    Prey(const InheritedTraits& inherited_traits);

    void eat_for_day(size_t food_amount);
    void reproduce(Prey* mate, std::vector<Prey*> prey);

    size_t get_strength();
    size_t get_calorie_count();
    void eaten();
};

class Predator : public Organism {
private:
    static SpeciesStatus species_status;

public:
    static Predator* get_new();
    static Predator* get_new_with_traits(const InheritedTraits& inherited_traits);

    Predator();
    Predator(const InheritedTraits& inherited_traits);

    void eat_for_day(std::vector<Prey*> prey);
    void reproduce(Predator* mate, std::vector<Predator*> predators);
};

