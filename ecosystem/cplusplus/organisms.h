#include <vector>


struct InheritedTraits {
    unsigned int strength;
    unsigned int offspring_capacity;
    float calorie_usage;

    InheritedTraits();
    InheritedTraits(unsigned int _strength, unsigned int _offspring_capacity, float _calorie_usage);
    InheritedTraits(const InheritedTraits& inherited_traits);
    void operator=(const InheritedTraits& inherited_traits);
};


enum OrganismType {PREY, PREDATOR};


class Organism {

};

class Prey : public Organism {
    void eat_for_day(uint food_amount);
};

class Predator : public Organism {
    void eat_for_day(std::vector<Prey> prey);
};

