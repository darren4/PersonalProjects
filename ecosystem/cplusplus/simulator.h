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
		std::vector<Prey>& surviving_prey,
		std::vector<Predator>& surviving_predators);

	// TODO: remove duplicate logic
	std::vector<Prey> reproduce_prey(std::vector<Prey> prey);
	std::vector<Predator> reproduce_predators(std::vector<Predator> predators);

	void move_prey(size_t row, size_t col, std::vector<Prey> prey);
	void move_predators(size_t row, size_t col, std::vector<Predator> predators);

	void wait_for_processing();
	void play_out_day(size_t row, size_t col);
	void check_and_display_status();
	void transition_and_set_to_process();

	void process_position(size_t row, size_t col);
public:
	void run_simulation();
};
