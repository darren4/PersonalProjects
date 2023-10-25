#include "organisms.h"

#include <mutex>
#include <condition_variable>


class Simulator {
private:
	unsigned int ready;
	std::mutex ready_mutex;
	std::condition_variable ready_cv;

	unsigned int worker_count;
	enum WorkerState {PROCESS, TRANSITION, DONE};
	WorkerState worker_state;
	std::mutex worker_state_mutex;
	std::condition_variable worker_state_cv;

	Planet planet;
	unsigned int day_count;

	void populate_survivors(PlanetPositionState& pos,
		std::vector<Prey>& surviving_prey,
		std::vector<Predator>& surviving_predators);

	template <typename T>
	std::vector<T> reproduce(const std::vector<T>& organisms) {

	}

	template <typename T>
	void move_organisms(unsigned int row, unsigned int col,
		const std::vector<T>& organisms, OrganismType organism_type) {

	}

	void wait_for_processing();
	void play_out_day(unsigned int row, unsigned int col);
	void check_and_display_status();
	void transition_and_set_to_process();

	void process_position(unsigned int row, unsigned int col);
public:
	Simulator();
	void run_simulation();
};
