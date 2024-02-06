from distributed_systems.framework import ProcessFramework, DistributedSystem
from distributed_systems.base_process import Msg, Process

import time
import sys


DONE = "DONE"

MANAGER_ID = 0
GUARD_ID = 1
WORKER_0_ID = 2
WORKER_1_ID = 3

WORKER_COUNT = 2


class Manager(Process):
    def start(self):
        super().start()
        ProcessFramework.output = 0
        bite_size = 5
        input_len = len(ProcessFramework.input)
        for window_start in range(0, input_len, bite_size):
            window_end = min(window_start + bite_size, input_len)
            msg: Msg = self.get_one_msg()
            self.send_msg(msg.src, Msg.build_msg(f"{window_start}~{window_end}"))
        for _ in range(WORKER_COUNT):
            msg = self.get_one_msg()
            self.send_msg(msg.src, Msg.build_msg(DONE))
        self.send_msg(GUARD_ID, Msg.build_msg(DONE))
        self.complete()


class Guard(Process):
    def start(self):
        super().start()
        self.owner = None
        while True:
            msg = self.get_one_msg()
            if msg.content and msg.content == DONE:
                break
            else:
                if not self.owner:
                    self.owner = msg.src
                    self.send_msg(msg.src, Msg.build_msg("TRUE"))
                elif self.owner == msg.src:
                    self.owner = None
                else:
                    self.send_msg(msg.src, Msg.build_msg("FALSE"))
        self.complete()


class Worker(Process):
    def _process_window(self, bounds: tuple):
        input_window = ProcessFramework.input[bounds[0] : bounds[1]]
        one_count = 0
        for char in input_window:
            if char == "1":
                one_count += 1

        holding_lock = False
        while not holding_lock:
            self.send_msg(GUARD_ID, Msg.build_msg())
            msg = self.get_one_msg()
            assert msg.src == GUARD_ID
            if msg.content == "TRUE":
                holding_lock = True
        ProcessFramework.output += one_count
        self.send_msg(GUARD_ID, Msg.build_msg())

    def start(self):
        super().start()
        while True:
            self.send_msg(MANAGER_ID, Msg.build_msg())
            msg = self.get_one_msg()
            msg_content: str = msg.content
            if msg.content == DONE:
                self.complete()
                break
            elif msg_content.find("~") != -1:
                range_list = msg_content.split("~")
                self._process_window((int(range_list[0]), int(range_list[1])))
            else:
                print(f"[DEBUG] Unrecognized message: {msg.content}")
                sys.exit()


if __name__ == "__main__":
    system_input = "000101111000010010000101111000010010"
    print(f"Input length: {len(system_input)}")
    processes = [
        Manager,
        Guard,
        Worker,
        Worker,
    ]
    DistributedSystem.define_faults(0.0, 0, float("inf"))
    start_time = time.time()
    DistributedSystem.process_input(system_input, processes)
    output = DistributedSystem.wait_for_completion()
    print(f"Runtime: {time.time() - start_time}")

    correct_count = 0
    for char in system_input:
        if char == "1":
            correct_count += 1
    assert output == correct_count