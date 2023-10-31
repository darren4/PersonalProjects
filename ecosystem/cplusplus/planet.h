#pragma once

#include "organisms.h"

#include <vector>
#include <mutex>


struct PlanetPositionState {
    std::vector<Predator*> predators;
    std::vector<Prey*> prey;
    size_t food;

    PlanetPositionState();
    PlanetPositionState(const PlanetPositionState& other);
    PlanetPositionState operator=(const PlanetPositionState& other);
};

struct PlanetPositionAccess {
    std::unique_lock<std::mutex> lock;
    PlanetPositionState ref;

    PlanetPositionAccess();
    PlanetPositionAccess(std::mutex& _mutex_ref,
        PlanetPositionState _position_ref);
    PlanetPositionAccess(const PlanetPositionAccess& other);
    PlanetPositionAccess operator=(const PlanetPositionAccess& other);
};

struct PlanetPosition {
    std::mutex current_lock;
    PlanetPositionState current;
    std::mutex next_lock;
    PlanetPositionState next;

    PlanetPosition();
    PlanetPosition(const PlanetPosition& other);
    PlanetPosition operator=(const PlanetPosition& other);
};

class Planet {
private:
    size_t height;
    size_t width;
    std::vector<std::vector<PlanetPosition>> grid;
public:
    Planet();
    Planet(size_t _height, size_t _width);
    Planet(const Planet& other);
    Planet operator=(const Planet& other);

    size_t get_height();
    size_t get_width();

    PlanetPositionAccess write_current(size_t row, size_t col);
    PlanetPositionAccess write_next(size_t row, size_t col);
};