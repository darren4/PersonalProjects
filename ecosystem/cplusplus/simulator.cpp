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
#include <cassert>
#include <stdio.h>

using std::cout;
using std::endl;
using std::vector;


Simulator::Simulator() : ready(0), worker_count(PLANET_GRID_HEIGHT * PLANET_GRID_WIDTH), 
                         worker_state(WorkerState::PROCESS),
                         planet(Planet(PLANET_GRID_HEIGHT, PLANET_GRID_WIDTH)), day_count(DAY_COUNT) {}

void Simulator::wait_for_processing() {
    std::unique_lock<std::mutex> worker_state_lock(worker_state_mutex);
    worker_state_cv.wait(worker_state_lock, [this] { return worker_state == WorkerState::PROCESS; });
}

void Simulator::populate_survivors(const PlanetPositionAccess& pos,
                                vector<Prey*>& surviving_prey,
                                vector<Predator*>& surviving_predators) {
    size_t prey_count = pos.get_prey_ptr()->size();
    size_t predator_count = pos.get_predators_ptr()->size();
    if (predator_count > 0) {
        vector<std::pair<Predator*, vector<Prey*>>> predators_to_prey;
        for (Predator* predator : *pos.get_predators_ptr()) {
            predators_to_prey.push_back(std::make_pair(predator, vector<Prey*>()));
        }
        if (prey_count < predator_count) {
            for (size_t prey_idx = 0; prey_idx < prey_count; ++prey_idx) {
                predators_to_prey[prey_idx].second.push_back((*pos.get_prey_ptr())[prey_idx]);
            }
        }
        else {
            size_t predator_idx = 0;
            for (size_t prey_idx = 0; prey_idx < prey_count; ++prey_idx) {
                if (predator_idx == predator_count) {
                    predator_idx = 0;
                }
                predators_to_prey[predator_idx].second.push_back((*pos.get_prey_ptr())[prey_idx]);
                ++predator_idx;
            }
        }
        for (std::pair<Predator*, vector<Prey*>> predator_prey : predators_to_prey) {
            predator_prey.first->eat_for_day(predator_prey.second);
            if (predator_prey.first->still_alive()) {
                surviving_predators.push_back(predator_prey.first);
            }
            else {
                delete predator_prey.first;
            }
        }
    }

    for (Prey* one_prey : *pos.get_prey_ptr()) {
        if (one_prey->still_alive()) {
            one_prey->eat_for_day(*pos.get_food_ptr());
            if (one_prey->still_alive()) {
                surviving_prey.push_back(one_prey);
            }
            else {
                delete one_prey;
            }
        }
    }
}

template <class T>
void Simulator::reproduce_organisms(std::vector<T*>& organisms) {
    size_t organism_count = organisms.size();
    for (size_t org_right_idx = 1; org_right_idx < organism_count; org_right_idx += 2) {
        organisms[org_right_idx - 1]->reproduce(organisms[org_right_idx], organisms);
    }
}
template void Simulator::reproduce_organisms(std::vector<Prey*>& organisms);
template void Simulator::reproduce_organisms(std::vector<Predator*>& organisms);

std::pair<size_t, size_t> Simulator::get_next_location(size_t row, size_t col) {
    vector<std::pair<size_t, size_t>> valid_positions;
    size_t planet_height = planet.get_height();
    size_t planet_width = planet.get_width();

    valid_positions.push_back({ row, col });
    if (row + 1 < planet_height && col + 1 < planet_width)
        valid_positions.push_back({ row + 1, col + 1 });
    if (row + 1 < planet_height)
        valid_positions.push_back({ row + 1, col });
    if (row + 1 < planet_height && col >= 1)
        valid_positions.push_back({ row + 1, col - 1 });
    if (col >= 1)
        valid_positions.push_back({ row, col - 1 });
    if (row >= 1 && col >= 1)
        valid_positions.push_back({ row - 1, col - 1 });
    if (row >= 1)
        valid_positions.push_back({ row - 1 , col });
    if (row >= 1 && col + 1 < planet_width)
        valid_positions.push_back({ row - 1, col + 1 });
    if (col + 1 < planet_width)
        valid_positions.push_back({ row, col + 1 });

    size_t random_position = random_int(0, valid_positions.size() - 1);
    std::pair<size_t, size_t> new_pos = valid_positions[random_position];
    assert(new_pos.first >= 0 && new_pos.first < planet_height && new_pos.second >= 0 && new_pos.second < planet_width);
    return new_pos;
}

void Simulator::play_out_day(size_t row, size_t col, vector<Prey*>& next_prey, vector<Predator*>& next_predators) {
    PlanetPositionAccess pos = planet.write(row, col);

    populate_survivors(pos, next_prey, next_predators);

    reproduce_organisms(next_prey);
    reproduce_organisms(next_predators);

    pos.get_prey_ptr()->clear();
    pos.get_predators_ptr()->clear();
}

bool Simulator::get_ecosystem_status() {
    return true;
}

void Simulator::set_worker_state(WorkerState next_worker_state, bool check_ecosystem_health) {
    std::unique_lock<std::mutex> ready_count_lock(ready_mutex);
    ++ready;
    if (ready == worker_count) {
        ready = 0;
        if (check_ecosystem_health && !get_ecosystem_status()) {
            next_worker_state = WorkerState::DONE;
        }
        std::unique_lock<std::mutex> worker_state_lock(worker_state_mutex);
        worker_state = next_worker_state;
        worker_state_cv.notify_all();
    }
}

PlanetPositionAccess Simulator::prepare_organism_move(size_t current_row, size_t current_col) {
    std::pair<size_t, size_t> next_row_col = get_next_location(current_row, current_col);
    return planet.write(next_row_col.first, next_row_col.second);
}

bool Simulator::transition_day(size_t row, size_t col, const std::vector<Prey*>& next_prey, const std::vector<Predator*>& next_predators) {
    std::unique_lock<std::mutex> worker_state_lock(worker_state_mutex);
    worker_state_cv.wait(worker_state_lock, [this] { return worker_state != WorkerState::PROCESS; });
    if (worker_state == WorkerState::DONE) {
        return false;
    }
    else if (worker_state == WorkerState::TRANSITION) {
        for (Prey* one_prey : next_prey) {
            PlanetPositionAccess access = prepare_organism_move(row, col);
            access.get_prey_ptr()->push_back(one_prey);
        }
        for (Predator* one_predator : next_predators) {
            PlanetPositionAccess access = prepare_organism_move(row, col);
            access.get_predators_ptr()->push_back(one_predator);
        }
        return true;
    }
    else {
        assert(false);
    }
}

void Simulator::process_position(size_t row, size_t col) {
    for (size_t day = 0; day < day_count; ++day) {
        wait_for_processing();

        vector<Prey*> next_prey;
        vector<Predator*> next_predators;
        play_out_day(row, col, next_prey, next_predators);

        set_worker_state(WorkerState::TRANSITION, true);

        if (transition_day(row, col, next_prey, next_predators)) {
            set_worker_state(WorkerState::PROCESS, false);
        }
        else {
            return;
        }
    }
}

void Simulator::run_simulation(){
    cout << "Initializing simulation\n";
    srand(0);

    for (size_t i = 0; i < START_FOOD_SOURCE_COUNT; ++i) {
        size_t row = random_int(0, PLANET_GRID_HEIGHT - 1);
        size_t col = random_int(0, PLANET_GRID_WIDTH - 1);
        PlanetPositionAccess access = planet.write(row, col);
        *access.get_food_ptr() += 1;
    }

    for (size_t i = 0; i < START_PREY_COUNT; ++i){
        size_t row = random_int(0, PLANET_GRID_HEIGHT - 1);
        size_t col = random_int(0, PLANET_GRID_WIDTH - 1);
        PlanetPositionAccess access = planet.write(row, col);
        access.get_prey_ptr()->push_back(Prey::get_new());
    }

    for (size_t i = 0; i < START_PREDATOR_COUNT; ++i){
        size_t row = random_int(0, PLANET_GRID_HEIGHT - 1);
        size_t col = random_int(0, PLANET_GRID_WIDTH - 1);
        PlanetPositionAccess access = planet.write(row, col);
        access.get_predators_ptr()->push_back(Predator::get_new());
    }
    
    cout << "Starting workers\n";
    vector<std::thread> threads;
    threads.reserve(worker_count);
    for (size_t row = 0; row < PLANET_GRID_HEIGHT; ++row) {
        for (size_t col = 0; col < PLANET_GRID_HEIGHT; ++col) {
            threads.push_back(std::thread(&Simulator::process_position, this, row, col));
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
