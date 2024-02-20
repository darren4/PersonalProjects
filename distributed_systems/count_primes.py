"""
Goal: Have threads keep each other alive while counting primes

Known Issues: 
    - At least one thread often does not finish even after processing complete
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
            json_dict["parent_counter"], json_dict["process_next"], json_dict["revival"]
        )

class Counter(Process):
    def initialize_state(self):
        self.counter_type: str = None
        self.revival: bool = None
        self.process_start: int = None
        self.process_end: int = None
        self.send_heartbeats_to: int = None
        self.get_heartbeats_from: int = None
        self.next_process_start: int = None
        self.next_process_end: int = None

    def process_startup_msg(self, startup_msg_str: str=None) -> bool:
        startup_msg: StartupMsg = StartupMsg.from_json(startup_msg_str)
        self.revival = startup_msg.revival == "TRUE"
        self.process_start = startup_msg.process_start
        self.send_heartbeats_to = startup_msg.parent_counter
        return False

    def start(self, startup_msg_str: str=None):
        self.initialize_state()
        if self.process_startup_msg(startup_msg_str):
            self.complete()
            return
        
        self.send_heartbeats_to_process(self.send_heartbeats_to)

        

class FirstCounter(Counter):
    def process_startup_msg(self, startup_msg_str: str=None) -> bool:
        if self.input <= BITE_SIZE:
            self.output = count_primes(0, self.input)
            return True
        self.revival = False
        self.process_start = 0
        self.send_heartbeats_to = math.ceil(self.input / BITE_SIZE) - 1
        return False

class Counter(Process):
    def initialize_state(self):
        self.revival: bool = None
        self.process_start: int = None
        self.process_end: int = None
        self.send_heartbeats_to: int = None
        self.get_heartbeats_from: int = None
        self.next_process_start: int = None
        self.next_process_end: int = None

    def start(self, startup_msg_str: str = None):
        self.initialize_state()
        
        if self.input <= BITE_SIZE:
            self.output = count_primes(0, self.input)
            return
        if not startup_msg_str:
            # First counter
            self.revival = False
            self.process_start = 0
            self.send_heartbeats_to = math.ceil(self.input / BITE_SIZE) - 1
        else:
            # All counters but first
            startup_msg: StartupMsg = StartupMsg.from_json(startup_msg_str)
            self.revival = startup_msg.revival == "TRUE"
            self.process_start = startup_msg.process_start
            self.send_heartbeats_to = startup_msg.parent_counter

        self.send_heartbeats_to_process(self.send_heartbeats_to)

        self.process_end = self.process_start + BITE_SIZE
        self.next_process_start = self.process_end
        self.next_process_end = self.next_process_start + BITE_SIZE
        if self.next_process_end >= self.input:
            # Last counter
            self.next_process_end = self.input
            self.get_heartbeats_from = 0
            revival_startup_msg = StartupMsg(self.get_id(), 0, "TRUE")
        else:
            # All counters but last
            self.get_heartbeats_from = self.get_id() + 1    
            regular_startup_msg = StartupMsg(self.get_id(), self.next_process_start)
            self.new_process(self.get_heartbeats_from, Counter, regular_startup_msg.to_json())
            revival_startup_msg = StartupMsg(self.get_id(), self.next_process_start, "TRUE")
        self.keep_process_alive(self.get_heartbeats_from, Counter, revival_startup_msg.to_json())

class FirstCounter(Process):
    def start(self, startup_msg_str: str = None):
        if startup_msg_str:
            startup_msg: StartupMsg = StartupMsg.from_json(startup_msg_str)
        else:
            startup_msg = StartupMsg(0, 0, "FALSE")
        if self.input < BITE_SIZE:
            self.output = count_primes(0, self.input)
        else:
            self.send_heartbeats_to_process(math.ceil(self.input / BITE_SIZE) - 1)

            next_counter_id = self.get_id() + 1
            count_range_start = 0
            count_range_end = count_range_start + BITE_SIZE
            next_counter_startup_msg = StartupMsg(
                self.get_id(), count_range_end
            ).to_json()
            if count_range_end + BITE_SIZE > self.input:
                if startup_msg.revival == "FALSE":
                    self.new_process(
                        next_counter_id, LastCounter, next_counter_startup_msg
                    )
                next_counter_startup_msg = StartupMsg(
                    self.get_id(), count_range_end, "TRUE"
                ).to_json()
                self.keep_process_alive(
                    next_counter_id, LastCounter, next_counter_startup_msg
                )
            else:
                if startup_msg.revival == "FALSE":
                    self.new_process(
                        next_counter_id, MiddleCounter, next_counter_startup_msg
                    )
                next_counter_startup_msg = StartupMsg(
                    self.get_id(), count_range_end, "TRUE"
                ).to_json()
                self.keep_process_alive(
                    next_counter_id, MiddleCounter, next_counter_startup_msg
                )

            prime_count = count_primes(count_range_start, count_range_end)

            msg: Msg = self.get_one_msg()
            if not msg.src == next_counter_id:
                raise RuntimeError(
                    f"Got message from {msg.src} when it should have been {next_counter_id}"
                )
            ProcessFramework.output = prime_count + int(msg.content)
            self.send_msg(next_counter_id, Msg.build_msg("DONE"))
        self.complete()


class MiddleCounter(Process):
    def start(self, startup_msg_str: str = None):
        startup_msg = StartupMsg.from_json(startup_msg_str)
        self.send_heartbeats_to_process(startup_msg.parent_counter)

        next_counter_id = self.get_id() + 1
        count_range_start = startup_msg.process_start
        count_range_end = count_range_start + BITE_SIZE
        next_counter_startup_msg = StartupMsg(self.get_id(), count_range_end).to_json()
        if count_range_end + BITE_SIZE > self.input:
            if startup_msg.revival == "FALSE":
                self.new_process(next_counter_id, LastCounter, next_counter_startup_msg)
            next_counter_startup_msg = StartupMsg(
                self.get_id(), count_range_end, "TRUE"
            ).to_json()
            self.keep_process_alive(
                next_counter_id, LastCounter, next_counter_startup_msg
            )
        else:
            if startup_msg.revival == "FALSE":
                self.new_process(
                    next_counter_id, MiddleCounter, next_counter_startup_msg
                )
            next_counter_startup_msg = StartupMsg(
                self.get_id(), count_range_end, "TRUE"
            ).to_json()
            self.keep_process_alive(
                next_counter_id, MiddleCounter, next_counter_startup_msg
            )

        prime_count = count_primes(count_range_start, count_range_end)

        msg: Msg = self.get_one_msg()
        if msg.src != next_counter_id:
            raise RuntimeError(
                f"Got message from {msg.src} when it should have been {next_counter_id}"
            )
        self.send_msg(
            startup_msg.parent_counter,
            Msg.build_msg(f"{prime_count + int(msg.content)}"),
        )
        msg: Msg = self.get_one_msg()
        if msg.src != startup_msg.parent_counter:
            raise RuntimeError(f"Expected message from parent but got {msg.src}")
        self.send_msg(next_counter_id, Msg.build_msg("DONE"))
        self.complete()


class LastCounter(Process):
    def start(self, startup_msg_str: str = None):
        startup_msg = StartupMsg.from_json(startup_msg_str)
        self.send_heartbeats_to_process(startup_msg.parent_counter)

        count_range_start = startup_msg.process_start
        count_range_end = min(count_range_start + BITE_SIZE, self.input)

        first_counter_startup_msg = StartupMsg(self.get_id(), 0, revival="TRUE").to_json()
        self.keep_process_alive(0, FirstCounter, first_counter_startup_msg)

        prime_count = count_primes(count_range_start, count_range_end)
        self.send_msg(startup_msg.parent_counter, Msg.build_msg(f"{prime_count}"))
        msg: Msg = self.get_one_msg()
        if msg.src != startup_msg.parent_counter:
            raise RuntimeError(f"Expected message from parent bug got {msg.src}")
        self.complete()


if __name__ == "__main__":
    system_input = 128834
    print(f"[SETUP] Input length: {system_input}")
    processes = [FirstCounter]
    start_time = time.time()
    DistributedSystem.define_faults(
        msg_drop_prop=0.0, max_process_kill_count=1, process_kill_wait_time=5
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
