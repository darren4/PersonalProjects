from distributed_systems.framework import ProcessFramework, DistributedSystem
from distributed_systems.base_process import Msg, Process, MsgType

import time
import math
from threading import Thread, Lock, Condition
import sys
import os


def check_prime(num):
    if num <= 1:
        return False
    for i in range(2, int(num / 2) + 1):
        if (num % i) == 0:
            return False
    return True


BITE_SIZE = 30000
DEFAULT_HEARTBEAT_WAIT = 2
DEFAULT_MAX_HEARTBEAT_WAIT = 6


class StartupMsg:
    def __init__(self, parent_worker, process_next):
        self.parent_worker = parent_worker
        self.process_next = process_next


class Worker(Process):
    def start(self, startup_msg: StartupMsg=None):
        super().start()

        first_worker = not startup_msg
        parent_worker = startup_msg.parent_worker
        if startup_msg.process_next >= self.input:
            last_worker = True
            maintain_worker = 0
        else:
            last_worker = False
            maintain_worker = self.get_id() + 1
        process_range = (startup_msg.process_next, min(self.input, startup_msg.process_next + BITE_SIZE))
        
        Thread(target=self.send_heartbeats, args=[parent_worker]).start()

        Thread(target=self.keep_worker_alive, args=[maintain_worker]).start()

        primes_in_range = self.count_primes(process_range)

        self.set_done_processing()

    def count_primes(self, process_range) -> int:
        answer = 0
        for input_value in range(process_range[0], process_range[1]):
            if check_prime(input_value):
                answer += 1
        return answer

    def keep_worker_alive(self, target, max_heartbeat_wait=DEFAULT_MAX_HEARTBEAT_WAIT):
        

    def send_heartbeats(self, target, wait_time=DEFAULT_HEARTBEAT_WAIT):
        while not self.check_done_processing():
            self.send_msg(target, Msg(self.get_id(), msg_type=MsgType.HEART, msg_content=None))
            time.sleep(wait_time)

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
    with open(f"{os.environ['PYTHONPATH']}/distributed_systems/output.txt", "w") as fh:
        if output == correct_count:
            fh.write("SUCCESS")
        else:
            fh.write("FAILURE")
