#pragma once

#include <vector>
#include <mutex>


struct InheritedTraits {
    size_t strength;
    size_t offspring_capacity;
    float calorie_usage;

    InheritedTraits();
    InheritedTraits(size_t _strength, size_t _offspring_capacity, float _calorie_usage);
    InheritedTraits(const InheritedTraits& other);
    InheritedTraits operator=(const InheritedTraits& other);
};

class SpeciesStatus {
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
    SpeciesStatus(const SpeciesStatus& other);
    SpeciesStatus operator=(const SpeciesStatus& other);

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
    Organism operator=(const Organism& other);

    bool still_alive();

    template<class T>
    void reproduce(T*, std::vector<T*> organisms);
};

class Prey : public Organism {
private:
    static SpeciesStatus species_status;

public:
    void eat_for_day(size_t food_amount);
    static Prey* new_prey();
    size_t get_strength();
    size_t get_calorie_count();
    void eaten();
};

class Predator : public Organism {
private:
    static SpeciesStatus species_status;

public:
    void eat_for_day(std::vector<Prey*> prey);
    static Predator* new_predator();
};

