#pragma once

#include "organisms.h"

#include <mutex>
#include <condition_variable>


class Simulator {
private:
	size_t ready;
	std::mutex ready_mutex;
	std::condition_variable ready_cv;

	size_t worker_count;
	enum WorkerState {PROCESS, TRANSITION, DONE};
	WorkerState worker_state;
	std::mutex worker_state_mutex;
	std::condition_variable worker_state_cv;

	Planet planet;
	size_t day_count;

	void populate_survivors(PlanetPositionState& pos,
		std::vector<Prey*>& surviving_prey,
		std::vector<Predator*>& surviving_predators);

	// TODO: move implementation elsewhere
	template <class T>
	void reproduce_organisms(std::vector<T*>& organisms) {
		size_t organism_count = organisms.size();
		for (size_t org_right_idx = 1; org_right_idx < organism_count; org_right_idx += 2) {
			organisms[org_right_idx - 1]->reproduce(organisms[org_right_idx], organisms);
		}
	}
	
	std::pair<size_t, size_t> get_next_location(size_t row, size_t col);

	PlanetPositionAccess prepare_organism_move(size_t current_row, size_t current_col);

	void wait_for_processing();
	void play_out_day(size_t row, size_t col);
	void check_and_display_status();
	void transition_and_set_to_process();

	void process_position(size_t row, size_t col);
public:
	void run_simulation();
};
