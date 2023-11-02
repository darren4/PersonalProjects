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
    SpeciesStatus(const SpeciesStatus& other) = delete;
    SpeciesStatus operator=(const SpeciesStatus& other) = delete;

    void reset_round();
};

class Organism {
protected:
    bool alive;
    size_t calorie_count;
    InheritedTraits traits;

    template<class T>
    size_t new_organisms(T*, std::vector<T*> organisms);

public:
    Organism();
    Organism(const Organism& other);
    Organism operator=(const Organism& other);

    bool still_alive();
};

class Prey : public Organism {
private:
    static SpeciesStatus species_status;

public:
    static Prey* new_prey();
    void eat_for_day(size_t food_amount);
    size_t get_strength();
    size_t get_calorie_count();
    void eaten();
    void reproduce(Prey*, std::vector<Prey*> prey);
};

class Predator : public Organism {
private:
    static SpeciesStatus species_status;

public:
    static Predator* new_predator();
    void eat_for_day(std::vector<Prey*> prey);
    void reproduce(Predator*, std::vector<Predator*> predators);
};

