#include <mutex>
#include <condition_variable>


class SimulatorWorkers {
private:
	static unsigned int ready;
	static std::mutex ready_mutex;
	static std::condition_variable ready_cv;

	static unsigned int worker_count;
	enum WorkerState {PROCESS, TRANSITION, DONE};
	static WorkerState worker_state;
	static std::mutex worker_state_mutex;
	static std::condition_variable worker_state_cv;

public:
	static void initialize_workers_state(unsigned int _worker_count, unsigned int _day_count);
	static void process_position(unsigned int row, unsigned int col);
};
