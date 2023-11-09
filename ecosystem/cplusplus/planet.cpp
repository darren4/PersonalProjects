#include "planet.h"

#include <cassert>


// --- PlanetPosition ---

PlanetPosition::PlanetPosition() : food(0) {}

void PlanetPosition::reset() {
    prey.clear();
    predators.clear();
}

// --- PlanetPositionAccess ---

PlanetPositionAccess::PlanetPositionAccess(PlanetPosition& _position_ref) : predators(&_position_ref.predators), prey(&_position_ref.prey), food(&_position_ref.food), position_mutex(&_position_ref.position_mutex) {
    position_mutex->lock();
}

PlanetPositionAccess& PlanetPositionAccess::operator=(const PlanetPositionAccess& other) {
    if (this == &other)
        return *this;

    predators = other.get_predators_ptr();
    prey = other.get_prey_ptr();
    food = other.get_food_ptr();
    position_mutex = other.get_position_mutex_ptr();

    return *this;
}

PlanetPositionAccess::~PlanetPositionAccess() {
    position_mutex->unlock();
}

std::vector<Predator*>* PlanetPositionAccess::get_predators_ptr() const {
    return predators;
}

std::vector<Prey*>* PlanetPositionAccess::get_prey_ptr() const {
    return prey;
}

size_t* PlanetPositionAccess::get_food_ptr() const {
    return food;
}

std::mutex* PlanetPositionAccess::get_position_mutex_ptr() const {
    return position_mutex;
}

// --- Planet ---

Planet::Planet() : height(0), width(0) {}

Planet::Planet(size_t _height, size_t _width)
    : height(_height), width(_width) {
    grid.reserve(_height);
    for (size_t row = 0; row < _height; ++row) {
        std::vector<PlanetPosition*> grid_row;
        grid_row.reserve(_width);
        for (size_t col = 0; col < _width; ++col) {
            grid_row.push_back(new PlanetPosition());
        }
        grid.push_back(grid_row);
    }
}

Planet::Planet(const Planet& other) : height(other.get_height()), width(other.get_width()), grid(other.get_grid()) {}

Planet& Planet::operator=(const Planet& other) {
    if (this == &other)
        return *this;

    height = other.get_height();
    width = other.get_width();
    grid = other.get_grid();

    return *this;
}

size_t Planet::get_height() const {
    return height;
}

size_t Planet::get_width() const {
    return width;
}

std::vector<std::vector<PlanetPosition*>> Planet::get_grid() const {
    return grid;
}

PlanetPositionAccess Planet::write(size_t row, size_t col) {
    assert(row >= 0 && row < height && col >= 0 && col < width);
    return PlanetPositionAccess(&grid[row][col]->position_mutex, &grid[row][col]->);
}

