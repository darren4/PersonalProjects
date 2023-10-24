#include "organisms.h"

#include <vector>
#include <shared_mutex>


struct PlanetPositionAccess{
    std::lock_guard<std::mutex> lock;
    PlanetPositionState& ref;
    PlanetPositionAccess(std::mutex& _mutex_ref, 
                        PlanetPositionState& _position_ref);
};

struct PlanetPositionState{
    std::vector<Predator> predators;
    std::vector<Prey> prey;
    unsigned int food;
};

struct PlanetPosition{
    std::mutex current_lock;
    PlanetPositionState current;
    std::mutex next_lock;
    PlanetPositionState next;
};

class Planet{
private:
    unsigned int height;
    unsigned int width;
    unsigned int worker_count;
    std::vector<std::vector<PlanetPosition>> grid;
public:
    Planet(unsigned int _height, unsigned int _width) 
        : height(_height), width(_width), worker_count(_height * _width) {
        PlanetPosition default_position;
        std::vector<PlanetPosition> grid_row;
        grid_row.resize(width, default_position);
        grid.resize(height, grid_row);

        
    }

    PlanetPositionAccess write_current(unsigned int row, unsigned int col);
    PlanetPositionAccess write_next(unsigned int row, unsigned int col);
    
};