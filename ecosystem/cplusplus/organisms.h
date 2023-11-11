#pragma once

#include "random_numbers.h"

#include <vector>
#include <mutex>
#include <algorithm>
#include <string>
#include <fstream>


struct InheritedTraits {
    size_t strength;
    size_t offspring_capacity;
    size_t calorie_usage;

    InheritedTraits();
    InheritedTraits(size_t _strength, size_t _offspring_capacity, size_t _calorie_usage);
    InheritedTraits(const InheritedTraits& other);
    InheritedTraits(const InheritedTraits& first, const InheritedTraits& second);
    InheritedTraits& operator=(const InheritedTraits& other);
    InheritedTraits& operator+=(const InheritedTraits& other);
    InheritedTraits& operator-=(const InheritedTraits& other);
};

class SpeciesStatus {
private:
    size_t round;
    std::string filename;
    std::ofstream filestream;

    std::mutex status_mutex;

    size_t alive_count;
    size_t created_in_round;
    size_t eaten_in_round;
    size_t starved_in_round;

    InheritedTraits inherited_traits_totals;

    void save_to_file();
    void reset_round();

public:
    SpeciesStatus();
    SpeciesStatus(const SpeciesStatus& other) = delete;
    SpeciesStatus operator=(const SpeciesStatus& other) = delete;

    void set_filename(std::string name);
    bool log_round_and_reset();

    void created(const InheritedTraits& organism_traits);
    void eaten(const InheritedTraits& organism_traits);
    void starved(const InheritedTraits& organism_traits);
};

class Organism {
protected:
    static SpeciesStatus status_of_organisms;
    bool alive;
    size_t calorie_count;
    InheritedTraits traits;

public:
    static void init_organism_logger();
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
    static void init_prey_logger();
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
    static void init_predator_logger();
    static bool log_predator_status();

    static Predator* get_new();
    static Predator* get_new_with_traits(const InheritedTraits& inherited_traits);

    Predator();
    Predator(const InheritedTraits& inherited_traits);

    void eat_for_day(std::vector<Prey*> prey);
    void reproduce(Predator* mate, std::vector<Predator*> predators);
};

