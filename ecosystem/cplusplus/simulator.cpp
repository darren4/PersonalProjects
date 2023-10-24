#include "organisms.h"
#include "planet.h"
#include "random_numbers.h"
#include "simulation_parameters.h"
#include "simulator_workers.h"

#include <vector>
#include <iostream>
#include <cstdlib>
#include <thread>

using std::cout;
typedef unsigned int uint;



void run_simulation(){
    cout << "Initializing simulation\n";
    srand(0);

    Planet planet(PLANET_GRID_HEIGHT, PLANET_GRID_WIDTH);

    for (uint i = 0; i < START_FOOD_SOURCE_COUNT; ++i) {
        uint row = random_int(0, PLANET_GRID_HEIGHT - 1);
        uint col = random_int(0, PLANET_GRID_WIDTH - 1);
        PlanetPositionAccess write_current = planet.write_current(row, col);
        write_current.ref.food += 1;
        PlanetPositionAccess write_next = planet.write_next(row, col);
        write_next.ref.food += 1;
    }

    for (uint i = 0; i < START_PREY_COUNT; ++i){
        uint row = random_int(0, PLANET_GRID_HEIGHT - 1);
        uint col = random_int(0, PLANET_GRID_WIDTH - 1);
        PlanetPositionAccess write_current = planet.write_current(row, col);
        Prey prey;
        write_current.ref.prey.push_back(prey);
    }

    for (uint i = 0; i < START_PREDATOR_COUNT; ++i){
        uint row = random_int(0, PLANET_GRID_HEIGHT - 1);
        uint col = random_int(0, PLANET_GRID_WIDTH - 1);
        PlanetPositionAccess write_current = planet.write_current(row, col);
        Predator predator;
        write_current.ref.predators.push_back(predator);
    }

    cout << "Starting workers\n";
    SimulatorWorkers::initialize_workers_state(PLANET_GRID_HEIGHT * PLANET_GRID_HEIGHT, DAY_COUNT);
    std::vector<std::thread> threads;
    for (uint row = 0; row < PLANET_GRID_HEIGHT; ++row) {
        for (uint col = 0; col < PLANET_GRID_HEIGHT; ++col) {
            std::thread t(SimulatorWorkers::process_position, row, col);
            threads.push_back(t);
        }
    }
    for (std::thread& t : threads) {
        t.join();
    }
    cout << "Simulation complete\n";
}

int main(){
    run_simulation();
    return 0;
}
