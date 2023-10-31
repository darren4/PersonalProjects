#pragma once

#include <vector>


struct InheritedTraits {
    size_t strength;
    size_t offspring_capacity;
    float calorie_usage;

    InheritedTraits();
    InheritedTraits(size_t _strength, size_t _offspring_capacity, float _calorie_usage);
    InheritedTraits(const InheritedTraits& inherited_traits);
    void operator=(const InheritedTraits& inherited_traits);
};


enum OrganismType {PREY, PREDATOR};


class Organism {
public:
    bool still_alive();

    template<class T>
    void reproduce(T*, std::vector<T*> organisms);
};

class Prey : public Organism {
public:
    void eat_for_day(size_t food_amount);
    static Prey* new_prey();
};

class Predator : public Organism {
public:
    void eat_for_day(std::vector<Prey*> prey);
    static Predator* new_predator();
};

