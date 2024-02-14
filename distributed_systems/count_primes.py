from distributed_systems.framework import ProcessFramework, DistributedSystem
from distributed_systems.base_process import Msg, Process, MsgType

import time
import math
from threading import Thread, Lock, Condition
import sys
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
    def __init__(self, parent_counter, process_next):
        self.parent_counter = parent_counter
        self.process_next = process_next

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(json_str: str):
        json_dict = json.loads(json_str)
        return StartupMsg(json_dict["parent_counter"], json_dict["process_next"])


class FirstCounter(Process):
    def start(self, startup_msg_str: str = None):
        if self.input < BITE_SIZE:
            self.output = count_primes(0, self.input)
        else:
            super().start_background_processing()

            self.send_heartbeats_to_process(math.ceil(self.input / BITE_SIZE) - 1)

            next_counter_id = self.get_id() + 1
            count_range_start = 0
            count_range_end = count_range_start + BITE_SIZE
            next_counter_startup_msg = StartupMsg(
                self.get_id(), count_range_end
            ).to_json()
            if count_range_end + BITE_SIZE > self.input:
                self.new_process(next_counter_id, LastCounter, next_counter_startup_msg)
                self.keep_process_alive(
                    next_counter_id, LastCounter, next_counter_startup_msg
                )
            else:
                self.new_process(
                    next_counter_id, MiddleCounter, next_counter_startup_msg
                )
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
        self.complete()


class MiddleCounter(Process):
    def start(self, startup_msg_str: str = None):
        super().start_background_processing()

        startup_msg = StartupMsg.from_json(startup_msg_str)
        self.send_heartbeats_to_process(startup_msg.parent_counter)

        next_counter_id = self.get_id() + 1
        count_range_start = startup_msg.process_next
        count_range_end = count_range_start + BITE_SIZE
        next_counter_startup_msg = StartupMsg(self.get_id(), count_range_end).to_json()
        if count_range_end + BITE_SIZE > self.input:
            self.new_process(next_counter_id, LastCounter, next_counter_startup_msg)
            self.keep_process_alive(
                next_counter_id, LastCounter, next_counter_startup_msg
            )
        else:
            self.new_process(next_counter_id, MiddleCounter, next_counter_startup_msg)
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
        self.complete()


class LastCounter(Process):
    def start(self, startup_msg_str: str = None):
        super().start_background_processing()

        startup_msg = StartupMsg.from_json(startup_msg_str)
        self.send_heartbeats_to_process(startup_msg.parent_counter)

        count_range_start = startup_msg.process_next
        count_range_end = min(count_range_start + BITE_SIZE, self.input)

        first_counter_startup_msg = StartupMsg(self.get_id(), 0).to_json()
        self.keep_process_alive(0, FirstCounter, first_counter_startup_msg)

        prime_count = count_primes(count_range_start, count_range_end)
        self.send_msg(startup_msg.parent_counter, Msg.build_msg(f"{prime_count}"))
        self.complete()


if __name__ == "__main__":
    system_input = 128834
    print(f"[SETUP] Input length: {system_input}")
    processes = [FirstCounter]
    start_time = time.time()
    DistributedSystem.define_faults(
        msg_drop_prop=0, max_process_kill_count=0, process_kill_wait_time=5
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
