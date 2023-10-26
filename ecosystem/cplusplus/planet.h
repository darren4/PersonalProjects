#pragma once

#include "organisms.h"

#include <vector>
#include <mutex>


struct PlanetPositionState{
    std::vector<Predator> predators;
    std::vector<Prey> prey;
    size_t food;
};

struct PlanetPositionAccess {
    std::unique_lock<std::mutex> lock;
    PlanetPositionState& ref;
    PlanetPositionAccess(std::mutex& _mutex_ref,
        PlanetPositionState& _position_ref);
};

struct PlanetPosition{
    std::mutex current_lock;
    PlanetPositionState current;
    std::mutex next_lock;
    PlanetPositionState next;
};

class Planet{
private:
    size_t height;
    size_t width;
    std::vector<std::vector<PlanetPosition>> grid;
public:
    Planet();
    Planet(size_t _height, size_t _width);

    PlanetPositionAccess write_current(size_t row, size_t col);
    PlanetPositionAccess write_next(size_t row, size_t col);
    
};