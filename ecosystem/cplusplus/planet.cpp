#include "planet.h"


Planet::Planet(unsigned int _height, unsigned int _width)
    : height(_height), width(_width) {
    PlanetPosition default_position;
    std::vector<PlanetPosition> grid_row;
    grid_row.resize(width, default_position);
    grid.resize(height, grid_row);
}
