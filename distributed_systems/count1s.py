from distributed_systems.framework import ProcessFramework, DistributedSystem
from distributed_systems.base_process import Msg, Process

import time
import math
from threading import Thread, Lock

BITE_SIZE = 5


class StartupMsg:
    def __init__(self, creator_id, next_to_process):
        self.creator_id = creator_id
        self.next_to_process = next_to_process


class Worker(Process):
    def initialize(self):
        self.verifier_id = None
        self.process_range = (None, None)
        self.first_worker = False
        self.last_worker = False
        self.wait_for = None

        self.next_worker_answer = None
        self.next_worker_answer_lock = Lock()

    def set_range(self, next_to_process=None):
        if not next_to_process:
            start = 0
            end = BITE_SIZE
        else:
            start = next_to_process
            end = next_to_process + BITE_SIZE
        if end >= len(self.input):
            end = len(self.input)
            self.last_worker = True
        self.process_range = (start, end)

    def send_heartbeats(self, target, wait_time=1):
        while not self.check_done_processing():
            self.send_msg(target, Msg(self.get_id(), msg_content=None))
            time.sleep(wait_time)

    def get_next_worker_results(self, worker_id, cutoff_time=5.0):
        while not self.check_done_processing():
            msg: Msg = self.get_one_msg(cutoff_time)
            if not msg:
                if worker_id == 0:
                    next_to_process = 0
                else:
                    next_to_process = self.process_range[1]
                try:
                    if not self.check_done_processing():
                        self.new_process(
                            Worker,
                            worker_id,
                            StartupMsg(self.get_id(), next_to_process),
                        )
                except ValueError:
                    continue
            elif msg.content is not None and not self.last_worker:
                with self.next_worker_answer_lock:
                    self.next_worker_answer = msg.content
                break

    def start(self, startup_msg: StartupMsg = None):
        super().start(startup_msg)
        self.initialize()

        if not startup_msg:
            self.first_worker = True
            self.verifier_id = math.ceil(len(self.input) / BITE_SIZE) - 1
            self.set_range()
        else:
            self.verifier_id = startup_msg.creator_id
            self.set_range(startup_msg.next_to_process)

        Thread(target=self.send_heartbeats, args=[self.verifier_id]).start()

        if not self.last_worker:
            startup_msg = StartupMsg(self.get_id(), self.process_range[1])
            self.wait_for = self.new_process(Worker, self.get_id() + 1, startup_msg)
        else:
            self.wait_for = 0
        get_next_t: Thread = Thread(
            target=self.get_next_worker_results, args=[self.wait_for]
        )
        get_next_t.start()

        answer = 0
        for idx in range(self.process_range[0], self.process_range[1]):
            if self.input[idx] == "1":
                answer += 1

        if not self.last_worker:
            get_next_t.join()
            with self.next_worker_answer_lock:
                answer += self.next_worker_answer

        if not self.first_worker:
            self.send_msg_verify(
                self.verifier_id, Msg(self.get_id(), msg_content=answer)
            )
        else:
            ProcessFramework.output = answer
        self.set_done_processing()


if __name__ == "__main__":
    system_input = "000101111000010010000101111000010010"
    print(f"Input length: {len(system_input)}")
    processes = [Worker]
    start_time = time.time()
    DistributedSystem.process_input(system_input, processes)
    output = DistributedSystem.wait_for_completion()
    print(f"Runtime: {time.time() - start_time}")

    correct_count = 0
    for char in system_input:
        if char == "1":
            correct_count += 1
    print(f"Correct: {correct_count}")
    print(f"Actual: {output}")
    assert output == correct_count
