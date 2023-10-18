

struct InheritedTraits {
    unsigned int strength;
    unsigned int offspring_capacity;
    float calorie_usage;

    InheritedTraits();
    InheritedTraits(unsigned int _strength, unsigned int _offspring_capacity, float _calorie_usage);
    InheritedTraits(const InheritedTraits& inherited_traits);
    void operator=(const InheritedTraits& inherited_traits);
};


class Organism {

};

class Prey : public Organism {

};

class Predator : public Organism {

};
