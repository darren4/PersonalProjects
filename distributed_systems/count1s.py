from distributed_systems.framework import ProcessFramework, DistributedSystem, SRC, MSG
from distributed_systems.base_process import Msg, Process

import time


DONE = "DONE"

MANAGER_ID = 0
GUARD_ID = 1
WORKER_0_ID = 2
WORKER_1_ID = 3

WORKER_COUNT = 2


class Manager(Process):
    def start(self, msg=None):
        super().start(msg)
        ProcessFramework.output = 0
        bite_size = 5
        input_len = len(ProcessFramework.input)
        for window_start in range(0, input_len, bite_size):
            window_end = min(window_start + bite_size, input_len)
            msg = self.get_one_msg()
            self.send_msg_verify(msg[SRC], Msg(msg_content=(window_start, window_end)))
        for _ in range(WORKER_COUNT):
            msg = self.get_one_msg()
            self.send_msg_verify(msg[SRC], Msg(msg_content=DONE))
        self.send_msg_verify(GUARD_ID, Msg(msg_content=DONE))
        self.set_done_processing()


class Guard(Process):
    def start(self, msg=None):
        super().start(msg)
        self.owner = None
        while True:
            src_and_msg = self.get_one_msg()
            src: int = int(src_and_msg[SRC])
            msg: Msg = src_and_msg[MSG]
            if msg.content and msg.content == DONE:
                break
            else:
                if not self.owner:
                    self.owner = src
                    self.send_msg_verify(src, Msg(msg_content=True))
                elif self.owner == src:
                    self.owner = None
                else:
                    self.send_msg_verify(src, Msg(msg_content=False))
        self.set_done_processing()


class Worker(Process):
    def _process_window(self, bounds):
        input_window = ProcessFramework.input[bounds[0] : bounds[1]]
        one_count = 0
        for char in input_window:
            if char == "1":
                one_count += 1

        holding_lock = False
        while not holding_lock:
            self.send_msg_verify(GUARD_ID, Msg())
            src_and_msg = self.get_one_msg()
            src: int = src_and_msg[SRC]
            msg: Msg = src_and_msg[MSG]
            assert src == GUARD_ID
            holding_lock = msg.content
        ProcessFramework.output += one_count
        self.send_msg_verify(GUARD_ID, Msg())

    def start(self, msg=None):
        super().start(msg)
        while True:
            self.send_msg_verify(MANAGER_ID, Msg())
            msg = self.get_one_msg()
            if msg[MSG].content == DONE:
                self.set_done_processing()
                break
            elif type(msg[MSG].content) == tuple:
                self._process_window(msg[MSG].content)
            else:
                print(f"[DEBUG] Unrecognized message: {msg[MSG].content}")


if __name__ == "__main__":
    system_input = "000101111000010010000101111000010010"
    print(f"Input length: {len(system_input)}")
    processes = [
        Manager,
        Guard,
        Worker,
        Worker,
    ]
    start_time = time.time()
    DistributedSystem.process_input(system_input, processes)
    output = DistributedSystem.wait_for_completion()
    print(f"Runtime: {time.time() - start_time}")

    correct_count = 0
    for char in system_input:
        if char == "1":
            correct_count += 1
    assert output == correct_count