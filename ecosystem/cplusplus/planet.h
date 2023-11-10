#pragma once

#include "organisms.h"

#include <vector>
#include <mutex>


struct PlanetPosition {
    std::mutex position_mutex;
    std::vector<Predator*> predators;
    std::vector<Prey*> prey;
    size_t food;

    PlanetPosition();
    PlanetPosition(const PlanetPosition& other) = delete;
    PlanetPosition& operator=(const PlanetPosition& other) = delete;
};

class PlanetPositionAccess {
private:
    std::vector<Predator*>* predators;
    std::vector<Prey*>* prey;
    size_t* food;
    std::mutex* position_mutex;

public:
    PlanetPositionAccess() = delete;
    PlanetPositionAccess(PlanetPosition& _position_ref);
    PlanetPositionAccess(const PlanetPositionAccess& other);
    PlanetPositionAccess& operator=(const PlanetPositionAccess& other);
    ~PlanetPositionAccess();

    std::vector<Predator*>* get_predators_ptr() const;
    std::vector<Prey*>* get_prey_ptr() const;
    size_t* get_food_ptr() const;
    std::mutex* get_position_mutex_ptr() const;
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

    PlanetPositionAccess write(size_t row, size_t col);
};