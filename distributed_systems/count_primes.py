from distributed_systems.framework import ProcessFramework, DistributedSystem
from distributed_systems.base_process import Msg, Process

import time
import math
from threading import Thread, Lock, Condition
import sys


def check_prime(num):
    if num <= 1:
        return False
    for i in range(2, int(num / 2) + 1):
        if (num % i) == 0:
            return False
    return True


BITE_SIZE = 40000
DEFAULT_HEARTBEAT_WAIT = 1
DEFAULT_MAX_HEARTBEAT_WAIT = 20


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
        self.next_worker_answer_cv = Condition(self.next_worker_answer_lock)

    def set_range(self, next_to_process=None):
        if not next_to_process:
            start = 0
            end = BITE_SIZE
        else:
            start = next_to_process
            end = next_to_process + BITE_SIZE
        if end >= self.input:
            end = self.input
            self.last_worker = True
        self.process_range = (start, end)

    def send_heartbeats(self, target, wait_time=DEFAULT_HEARTBEAT_WAIT):
        while not self.check_done_processing():
            self.send_msg(target, Msg(self.get_id(), msg_content=None))
            time.sleep(wait_time)

    def get_next_worker_results(
        self, worker_id, max_heartbeat_wait=DEFAULT_MAX_HEARTBEAT_WAIT
    ):
        while not self.check_done_processing():
            msg: Msg = self.get_one_msg(max_heartbeat_wait)
            if not msg:
                if worker_id == 0:
                    next_to_process = 0
                else:
                    next_to_process = self.process_range[1]
                if not self.check_done_processing():
                    print(f"[RECOVER] Reviving worker {worker_id}")
                    try:
                        self.new_process(
                            Worker,
                            worker_id,
                            StartupMsg(self.get_id(), next_to_process),
                        )
                    except ValueError:
                        print(f"[ERROR] Revived alive worker {worker_id}")
                        sys.exit()
            elif msg.content is not None and not self.last_worker:
                with self.next_worker_answer_lock:
                    self.next_worker_answer = msg.content
                    self.next_worker_answer_cv.notify()
                break

    def start(self, startup_msg: StartupMsg = None):
        super().start(startup_msg)
        self.initialize()

        if not startup_msg:
            self.first_worker = True
            self.verifier_id = math.ceil(self.input / BITE_SIZE) - 1
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
        for input_value in range(self.process_range[0], self.process_range[1]):
            if check_prime(input_value):
                answer += 1

        if not self.last_worker:
            with self.next_worker_answer_lock:
                while not self.next_worker_answer:
                    self.next_worker_answer_cv.wait()
                answer += self.next_worker_answer

        if not self.first_worker:
            self.send_msg_verify(
                self.verifier_id, Msg(self.get_id(), msg_content=answer)
            )
        else:
            ProcessFramework.output = answer
        self.set_done_processing()


if __name__ == "__main__":
    system_input = 128834
    print(f"[SETUP] Input length: {system_input}")
    processes = [Worker]
    start_time = time.time()
    DistributedSystem.process_input(system_input, processes)
    output = DistributedSystem.wait_for_completion()
    print(f"[RESULT] Runtime: {time.time() - start_time}")

    correct_count = 12059
    print(f"[RESULT] Correct: {correct_count}")
    print(f"[RESULT] Actual: {output}")
    assert output == correct_count
