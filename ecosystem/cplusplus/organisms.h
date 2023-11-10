#pragma once

#include "random_numbers.h"

#include <vector>
#include <mutex>
#include <algorithm>



struct InheritedTraits {
    size_t strength;
    size_t offspring_capacity;
    size_t calorie_usage;

    InheritedTraits();
    InheritedTraits(size_t _strength, size_t _offspring_capacity, size_t _calorie_usage);
    InheritedTraits(const InheritedTraits& other);
    InheritedTraits(const InheritedTraits& first, const InheritedTraits& second);
    InheritedTraits& operator=(const InheritedTraits& other);
};

class SpeciesStatus {
private:
    size_t alive_count;
    std::mutex alive_count_mutex;

    size_t created_in_round;
    std::mutex created_in_round_mutex;

    size_t eaten_in_round;
    std::mutex eaten_in_round_mutex;

    size_t starved_in_round;
    std::mutex starved_in_round_mutex;

    InheritedTraits inherited_traits_totals;

    void save_to_file();
    void reset_round();

public:
    SpeciesStatus();
    SpeciesStatus(const SpeciesStatus& other) = delete;
    SpeciesStatus operator=(const SpeciesStatus& other) = delete;

    void created(const InheritedTraits& organism_traits);
    void eaten(const InheritedTraits& organism_traits);
    void starved(const InheritedTraits& organism_traits);

    bool log_round_and_reset();
};

class Organism {
protected:
    static SpeciesStatus status_of_organisms;

    bool alive;
    size_t calorie_count;
    InheritedTraits traits;

public:
    static bool log_organism_status();

    Organism();
    Organism(const Organism& other) = delete;
    Organism(const InheritedTraits& inherited_traits);
    Organism operator=(const Organism& other) = delete;

    const InheritedTraits& get_traits() const;
    bool still_alive() const;
};

class Prey : public Organism {
private:
    static SpeciesStatus status_of_prey;

public:
    static bool log_prey_status();

    static Prey* get_new();
    static Prey* get_new_with_traits(const InheritedTraits& inherited_traits);

    Prey();
    Prey(const InheritedTraits& inherited_traits);

    void eat_for_day(size_t food_amount);
    void reproduce(Prey* mate, std::vector<Prey*> prey);

    size_t get_strength() const;
    size_t get_calorie_count() const;
    void eaten();
};

class Predator : public Organism {
private:
    static SpeciesStatus status_of_predators;

public:
    static bool log_predator_status();

    static Predator* get_new();
    static Predator* get_new_with_traits(const InheritedTraits& inherited_traits);

    Predator();
    Predator(const InheritedTraits& inherited_traits);

    void eat_for_day(std::vector<Prey*> prey);
    void reproduce(Predator* mate, std::vector<Predator*> predators);
};

