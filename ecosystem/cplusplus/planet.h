#pragma once

#include "organisms.h"

#include <vector>
#include <mutex>


struct PlanetPositionState {
    std::vector<Predator*> predators;
    std::vector<Prey*> prey;
    size_t food;

    PlanetPositionState();
    PlanetPositionState(const PlanetPositionState& other) = delete;
    PlanetPositionState& operator=(const PlanetPositionState& other) = delete;

    void get_organisms(const PlanetPositionState& other);
    void reset();
};

struct PlanetPositionAccess {
    std::mutex* ref_mutex;
    PlanetPositionState* ref;

    PlanetPositionAccess() = delete;
    PlanetPositionAccess(std::mutex* _ref_mutex,
        PlanetPositionState* _position_ref);
    PlanetPositionAccess(const PlanetPositionAccess& other);
    PlanetPositionAccess& operator=(const PlanetPositionAccess& other);
    ~PlanetPositionAccess();
};

struct PlanetPosition {
    std::mutex current_mutex;
    PlanetPositionState current;
    std::mutex next_mutex;
    PlanetPositionState next;

    PlanetPosition();
    PlanetPosition(const PlanetPosition& other) = delete;
    PlanetPosition& operator=(const PlanetPosition& other) = delete;
};

class Planet {
private:
    size_t height;
    size_t width;
    std::vector<std::vector<PlanetPosition*>> grid;
public:
    Planet();
    Planet(size_t _height, size_t _width);
    Planet(const Planet& other);
    Planet& operator=(const Planet& other);

    size_t get_height() const;
    size_t get_width() const;
    std::vector<std::vector<PlanetPosition*>> get_grid() const;

    PlanetPositionAccess write_current(size_t row, size_t col);
    PlanetPositionAccess write_next(size_t row, size_t col);
};