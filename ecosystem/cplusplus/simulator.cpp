#include "organisms.h"
#include "planet.h"
#include "random_numbers.h"
#include "simulation_parameters.h"
#include "simulator.h"
#include "organisms.h"

#include <vector>
#include <iostream>
#include <cstdlib>
#include <thread>
#include <mutex>
#include <algorithm>
#include <utility>

using std::cout;
using std::vector;

void Simulator::wait_for_processing() {
    std::unique_lock<std::mutex> worker_state_lock(worker_state_mutex);
    worker_state_cv.wait(worker_state_lock, [this] { return worker_state != WorkerState::PROCESS; });
}

void Simulator::populate_survivors(PlanetPositionState& pos,
                                vector<Prey>& surviving_prey,
                                vector<Predator>& surviving_predators) {
    std::random_shuffle(pos.prey.begin(), pos.prey.end());
    std::random_shuffle(pos.predators.begin(), pos.predators.end());

    size_t prey_count = pos.prey.size();
    size_t predator_count = pos.predators.size();
    if (predator_count > 0) {
        vector<std::pair<Predator, vector<Prey>>> predators_to_prey;
        for (Predator predator : pos.predators) {
            predators_to_prey.push_back(std::make_pair(predator, vector<Prey>()));
        }
        if (prey_count < predator_count) {
            for (size_t prey_idx = 0; prey_idx < prey_count; ++prey_idx) {
                predators_to_prey[prey_idx].second.push_back(pos.prey[prey_idx]);
            }
        }
        else {
            size_t predator_idx = 0;
            for (size_t prey_idx = 0; prey_idx < prey_count; ++prey_idx) {
                if (predator_idx == prey_idx) {
                    predator_idx = 0;
                }
                predators_to_prey[predator_idx].second.push_back(pos.prey[prey_idx]);
                ++predator_idx;
            }
        }
        for (std::pair<Predator, vector<Prey>> predator_prey : predators_to_prey) {
            predator_prey.first.eat_for_day(predator_prey.second);
            if (predator_prey.first.still_alive()) {
                surviving_predators.push_back(Predator(predator_prey.first));
            }
        }
    }

    for (Prey& one_prey : pos.prey) {
        if (one_prey.still_alive()) {
            one_prey.eat_for_day(pos.food);
            if (one_prey.still_alive()) {
                surviving_prey.push_back(Prey(one_prey));
            }
        }
    }
}

std::vector<Prey> Simulator::reproduce_prey(std::vector<Prey> prey) {

}
std::vector<Predator> Simulator::reproduce_predators(std::vector<Predator> predators) {

}

void Simulator::move_prey(size_t row, size_t col, std::vector<Prey> prey) {

}
void Simulator::move_predators(size_t row, size_t col, std::vector<Predator> predators) {

}

void Simulator::play_out_day(size_t row, size_t col) {
    PlanetPositionAccess pos = planet.write_current(row, col);
    vector<Prey> surviving_prey;
    vector<Predator> surviving_predators;
    populate_survivors(pos.ref, surviving_prey, surviving_predators);

    vector<Prey> next_prey = reproduce_prey(surviving_prey);
    vector<Predator> next_predators = reproduce_predators(surviving_predators);

    move_prey(row, col, next_prey);
    move_predators(row, col, next_predators);
}

void Simulator::process_position(size_t row, size_t col) {
    for (size_t day = 0; day < day_count; ++day) {
        wait_for_processing();

        play_out_day(row, col);

        check_and_display_status();

        transition_and_set_to_process();
    }
}

Simulator::Simulator() : ready(0), worker_count(0), worker_state(WorkerState::PROCESS), day_count(0) {}

void Simulator::run_simulation(){
    cout << "Initializing simulation\n";
    srand(0);

    Planet _planet(PLANET_GRID_HEIGHT, PLANET_GRID_WIDTH);
    planet = _planet;

    for (size_t i = 0; i < START_FOOD_SOURCE_COUNT; ++i) {
        size_t row = random_int(0, PLANET_GRID_HEIGHT - 1);
        size_t col = random_int(0, PLANET_GRID_WIDTH - 1);
        PlanetPositionAccess write_current = planet.write_current(row, col);
        write_current.ref.food += 1;
        PlanetPositionAccess write_next = planet.write_next(row, col);
        write_next.ref.food += 1;
    }

    for (size_t i = 0; i < START_PREY_COUNT; ++i){
        size_t row = random_int(0, PLANET_GRID_HEIGHT - 1);
        size_t col = random_int(0, PLANET_GRID_WIDTH - 1);
        PlanetPositionAccess write_current = planet.write_current(row, col);
        Prey prey;
        write_current.ref.prey.push_back(prey);
    }

    for (size_t i = 0; i < START_PREDATOR_COUNT; ++i){
        size_t row = random_int(0, PLANET_GRID_HEIGHT - 1);
        size_t col = random_int(0, PLANET_GRID_WIDTH - 1);
        PlanetPositionAccess write_current = planet.write_current(row, col);
        Predator predator;
        write_current.ref.predators.push_back(predator);
    }

    cout << "Starting workers\n";
    worker_count = PLANET_GRID_HEIGHT * PLANET_GRID_HEIGHT;
    day_count = DAY_COUNT;
    vector<std::thread> threads;
    for (size_t row = 0; row < PLANET_GRID_HEIGHT; ++row) {
        for (size_t col = 0; col < PLANET_GRID_HEIGHT; ++col) {
            std::thread t(process_position, row, col);
            threads.push_back(t);
        }
    }
    for (std::thread& t : threads) {
        t.join();
    }
    cout << "Simulation complete\n";
}

int main(){
    Simulator simulator;
    simulator.run_simulation();
    return 0;
}
