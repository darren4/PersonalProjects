#pragma once

#include "organisms.h"

#include <mutex>
#include <condition_variable>


class Simulator {
private:
	static size_t ready;
	static std::mutex ready_mutex;
	static std::condition_variable ready_cv;

	static size_t worker_count;
	enum WorkerState {PROCESS, TRANSITION, DONE};
	static WorkerState worker_state;
	static std::mutex worker_state_mutex;
	static std::condition_variable worker_state_cv;

	static Planet planet;
	static size_t day_count;

	static void populate_survivors(PlanetPositionState& pos,
		std::vector<Prey>& surviving_prey,
		std::vector<Predator>& surviving_predators);

	// TODO: remove duplicate logic
	static std::vector<Prey> reproduce_prey(std::vector<Prey> prey);
	static std::vector<Predator> reproduce_predators(std::vector<Predator> predators);

	static void move_prey(size_t row, size_t col, std::vector<Prey> prey);
	static void move_predators(size_t row, size_t col, std::vector<Predator> predators);

	static void wait_for_processing();
	static void play_out_day(size_t row, size_t col);
	static void check_and_display_status();
	static void transition_and_set_to_process();

	static void process_position(size_t row, size_t col);
public:
	static void run_simulation();
};
