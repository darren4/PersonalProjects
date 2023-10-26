#include "planet.h"


Planet::Planet(size_t _height, size_t _width)
    : height(_height), width(_width) {
    PlanetPosition default_position;
    std::vector<PlanetPosition> grid_row;
    grid_row.resize(width, default_position);
    grid.resize(height, grid_row);
}
