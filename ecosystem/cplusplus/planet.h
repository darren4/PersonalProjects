#include <vector>
#include <mutex>

using std::mutex;


struct PlanetPositionState{
    
};

struct PlanetPosition{
    mutex current_lock;
    PlanetPositionState current;
    mutex next_lock;
    PlanetPositionState next;
};

class Planet{
private:
    unsigned int height;
    unsigned int width;
    vector<vector<PlanetPosition>> grid;
public:
    Planet(unsigned int _height, unsigned int _width) 
        : height(_height), width(_width) {
        PlanetPosition default_position();

        vector<PlanetPosition> grid_row;
        grid_row.resize(width, default_position);

        grid.resize(height, grid_row);
    }
} global_planet;