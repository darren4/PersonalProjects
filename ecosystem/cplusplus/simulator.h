#pragma once

#include "organisms.h"
#include "planet.h"

#include <mutex>
#include <condition_variable>


class Simulator {
private:
	size_t ready;
	std::mutex ready_mutex;
	std::condition_variable ready_cv;

	const size_t worker_count;
	enum WorkerState {PROCESS, TRANSITION, DONE};
	WorkerState worker_state;
	std::mutex worker_state_mutex;
	std::condition_variable worker_state_cv;

	Planet planet;
	size_t day_count;

	void populate_survivors(const PlanetPositionAccess& pos,
		std::vector<Prey*>& surviving_prey,
		std::vector<Predator*>& surviving_predators);

	template <class T>
	void reproduce_organisms(std::vector<T*>& organisms);
	
	std::pair<size_t, size_t> get_next_location(size_t row, size_t col);

	PlanetPositionAccess prepare_organism_move(size_t current_row, size_t current_col);

	bool get_ecosystem_status();

	void wait_for_processing();
	void play_out_day(size_t row, size_t col, std::vector<Prey*>& next_prey, std::vector<Predator*>& next_predators);
	void set_worker_state(WorkerState next_worker_state, bool check_ecosystem_health);
	bool transition_day(size_t row, size_t col, const std::vector<Prey*>& next_prey, const std::vector<Predator*>& next_predators);

	void process_position(size_t row, size_t col);
public:
	Simulator();
	void run_simulation();
};
