from distributed_systems.lib import BaseProcess, DistributedSystem, SRC, MSG

import time


DONE = "DONE"

MANAGER_ID = 0
GUARD_ID = 1
WORKER_0_ID = 2
WORKER_1_ID = 3

WORKER_COUNT = 2


class Process(BaseProcess):
    def get_one_message(self, wait_time=0.1):
        while True:
            msg = self.read_msg()
            if msg:
                return msg
            else:
                time.sleep(wait_time)


class Manager(Process):

    def start(self):
        BaseProcess.output = 0
        bite_size = 5
        input_len = len(BaseProcess.input)
        for window_start in range(0, input_len, bite_size):
            window_end = min(window_start + bite_size, input_len)
            msg = self.get_one_message()
            self.send_msg(msg[SRC], (window_start, window_end))
        for _ in range(WORKER_COUNT):
            msg = self.get_one_message()
            self.send_msg(msg[SRC], DONE)
        self.send_msg(GUARD_ID, DONE)
        self.complete()


class Guard(BaseProcess):
    def __init__(self, id):
        super().__init__(id)
        self.owner = None

    def start(self):
        while True:
            msg = self.read_msg()
            if msg:
                if msg[MSG] and msg[MSG] == DONE:
                    break
                else:
                    if not self.owner:
                        self.send_msg(int(msg[SRC]), True)
                        self.owner = int(msg[SRC])
                    elif self.owner == int(msg[SRC]):
                        self.owner = None
                    else:
                        self.send_msg(int(msg[SRC]), False)
            else:
                time.sleep(0.1)
        self.complete()


class Worker(Process):

    def _process_window(self, bounds):
        input_window = BaseProcess.input[bounds[0]: bounds[1]]
        one_count = 0
        for char in input_window:
            if char == "1":
                one_count += 1
        
        holding_lock = False
        while not holding_lock:
            self.send_msg(GUARD_ID)
            msg = self.get_one_message()
            assert msg[SRC] == GUARD_ID
            holding_lock = msg[MSG]
        BaseProcess.output += one_count
        self.send_msg(GUARD_ID)

    def start(self):
        while True:
            self.send_msg(MANAGER_ID)
            msg = self.get_one_message()
            if msg[MSG] == DONE:
                self.complete()
                return
            elif type(msg[MSG]) == tuple:
                self._process_window(msg[MSG])
            else:
                print(f"[DEBUG] Unrecognized message: {msg[MSG]}")


if __name__ == "__main__":
    system_input = "000101111000010010000101111000010010"
    processes = [
        Manager(MANAGER_ID),
        Guard(GUARD_ID),
        Worker(WORKER_0_ID),
        Worker(WORKER_1_ID),
    ]
    DistributedSystem.process_input(system_input, processes)
    DistributedSystem.wait_for_completion()

    correct_count = 0
    for char in system_input:
        if char == "1":
            correct_count += 1
    assert BaseProcess.output == correct_count
