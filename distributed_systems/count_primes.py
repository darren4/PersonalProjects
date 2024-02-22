"""
Goal: Have threads keep each other alive while counting primes
"""

from distributed_systems.framework import ProcessFramework, DistributedSystem
from distributed_systems.base_process import Msg, Process

import time
import math
import os
import json

BITE_SIZE = 30000


def check_prime(num):
    if num <= 1:
        return False
    for i in range(2, int(num / 2) + 1):
        if (num % i) == 0:
            return False
    return True


def count_primes(range_start, range_end):
    answer = 0
    for input_value in range(range_start, range_end):
        if check_prime(input_value):
            answer += 1
    return answer


class StartupMsg:
    def __init__(self, parent_counter: int, process_start: int, revival: str = "FALSE"):
        self.parent_counter: int = parent_counter
        self.process_start: int = process_start
        self.revival: str = revival

    def to_json(self) -> str:
        return json.dumps(vars(self))

    @staticmethod
    def from_json(json_str: str):
        json_dict = json.loads(json_str)
        return StartupMsg(
            json_dict["parent_counter"],
            json_dict["process_start"],
            json_dict["revival"],
        )


class Counter(Process):
    def initialize_state(self):
        self.counter_type: str = None
        self.revival: bool = None
        self.process_start: int = None
        self.process_end: int = None
        self.send_heartbeats_to: int = None
        self.get_heartbeats_from: int = None

    def process_startup_msg(self, startup_msg_str: str = None) -> bool:
        startup_msg: StartupMsg = StartupMsg.from_json(startup_msg_str)
        self.revival = startup_msg.revival == "TRUE"
        self.process_start = startup_msg.process_start
        self.send_heartbeats_to = startup_msg.parent_counter
        return False

    def keep_child_counter_alive(self):
        self.process_end = self.process_start + BITE_SIZE
        if self.process_end >= self.input:
            # Last counter
            self.process_end = self.input
            self.get_heartbeats_from = 0
            revival_startup_msg = StartupMsg(self.get_id(), 0, "TRUE")
        else:
            # All counters but last
            self.get_heartbeats_from = self.get_id() + 1
            regular_startup_msg = StartupMsg(self.get_id(), self.process_end)
            self.new_process(
                self.get_heartbeats_from, Counter, regular_startup_msg.to_json()
            )
            revival_startup_msg = StartupMsg(self.get_id(), self.process_end, "TRUE")
        self.keep_process_alive(
            self.get_heartbeats_from, Counter, revival_startup_msg.to_json()
        )

    def start(self, startup_msg_str: str = None):
        self.initialize_state()
        if self.process_startup_msg(startup_msg_str):
            self.complete()
            return

        self.send_heartbeats_to_process(self.send_heartbeats_to)

        self.keep_child_counter_alive()

        prime_count = count_primes(self.process_start, self.process_end)
        if self.get_heartbeats_from == 0:
            # Last counter
            final_prime_count = prime_count
        else:
            # All counters but last
            final_prime_count = None
        while True:
            if not final_prime_count:
                self.send_msg(self.get_heartbeats_from, Msg.build_msg("REQUEST"))

            msg = self.get_one_msg()
            if msg.content == "DONE":
                if self.get_heartbeats_from != 0:
                    self.send_msg(self.get_heartbeats_from, Msg.build_msg("DONE"))
                self.complete()
                return
            elif msg.content.isdigit():
                final_prime_count = int(msg.content) + prime_count
                if self.get_id() == 0:
                    ProcessFramework.output = final_prime_count
                    self.send_msg(self.get_heartbeats_from, Msg.build_msg("DONE"))
                    self.complete()
                    return
            elif msg.content == "REQUEST":
                if final_prime_count:
                    self.send_msg(msg.src, Msg.build_msg(f"{final_prime_count}"))
                else:
                    self.send_msg(msg.src, Msg.build_msg("WAIT"))
            elif msg.content == "WAIT":
                time.sleep(1)


class FirstCounter(Counter):
    def process_startup_msg(self, startup_msg_str: str = None) -> bool:
        if self.input <= BITE_SIZE:
            self.output = count_primes(0, self.input)
            return True
        self.revival = False
        self.process_start = 0
        self.send_heartbeats_to = math.ceil(self.input / BITE_SIZE) - 1
        return False


if __name__ == "__main__":
    system_input = 128834
    print(f"[SETUP] Input length: {system_input}")
    processes = [FirstCounter]
    start_time = time.time()
    DistributedSystem.define_faults(
        msg_drop_prop=0.0, max_process_kill_count=0, process_kill_wait_time=5
    )
    DistributedSystem.process_input(system_input, processes)
    output = DistributedSystem.wait_for_completion()
    print(f"[RESULT] Runtime: {time.time() - start_time}")

    correct_count = 12059
    print(f"[RESULT] Correct: {correct_count}")
    print(f"[RESULT] Actual: {output}")
    if output == correct_count:
        write_msg = "SUCCESS"
    else:
        write_msg = "FAIL"
    print(f"[FINAL RESULT] {write_msg}")
    with open(f"{os.environ['PYTHONPATH']}/distributed_systems/output.txt", "w") as fh:
        fh.write(write_msg)
