#include "organisms.h"

#include <vector>
#include <mutex>


struct PlanetPositionAccess{
    std::unique_lock<std::mutex> lock;
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
    std::vector<std::vector<PlanetPosition>> grid;
public:
    Planet();
    Planet(unsigned int _height, unsigned int _width);

    PlanetPositionAccess write_current(unsigned int row, unsigned int col);
    PlanetPositionAccess write_next(unsigned int row, unsigned int col);
    
};