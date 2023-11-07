#include "planet.h"


// --- PlanetPositionState ---

PlanetPositionState::PlanetPositionState() : food(0) {}

PlanetPositionState& PlanetPositionState::operator=(const PlanetPositionState& other) {
    if (this == &other) {
        return *this;
    }
    predators = other.predators;
    prey = other.prey;
    food = other.food;
    return *this;
}

// --- PlanetPositionAccess ---

PlanetPositionAccess::PlanetPositionAccess(std::mutex* _ref_mutex, PlanetPositionState* _position_ref) : ref_mutex(_ref_mutex), ref(_position_ref) {
    ref_mutex->lock();
}

PlanetPositionAccess::PlanetPositionAccess(const PlanetPositionAccess& other) : ref_mutex(other.ref_mutex), ref(other.ref) {}

PlanetPositionAccess& PlanetPositionAccess::operator=(const PlanetPositionAccess& other) {
    if (this == &other)
        return *this;

    ref = other.ref;
    ref_mutex = other.ref_mutex;

    return *this;
}

PlanetPositionAccess::~PlanetPositionAccess() {
    ref_mutex->unlock();
}

// --- PlanetPosition ---

PlanetPosition::PlanetPosition() {}

PlanetPosition& PlanetPosition::operator=(const PlanetPosition& other) {
    if (this == &other) {
        return *this;
    }
    current = other.current;
    next = other.next;
    return *this;
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

PlanetPositionAccess Planet::write_current(size_t row, size_t col) {
    return PlanetPositionAccess(&grid[row][col]->current_mutex, &grid[row][col]->current);
}

PlanetPositionAccess Planet::write_next(size_t row, size_t col) {
    return PlanetPositionAccess(&grid[row][col]->next_mutex, &grid[row][col]->next);
}
