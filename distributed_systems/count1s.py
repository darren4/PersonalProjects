from distributed_systems.framework import ProcessFramework, DistributedSystem, SRC, MSG
from distributed_systems.base_process import Msg, Process

import time

BITE_SIZE = 5


class StartupMsg:
    def __init__(self, creator_id, next_to_process):
        self.creator_id = creator_id
        self.next_to_process = next_to_process


class Worker(Process):
    def initialize(self):
        self.creator_id = None
        self.process_range = (None, None)
        self.last_worker = False

    def set_range(self, next_to_process=None):
        if not next_to_process:
            target_range = (0, BITE_SIZE)
        else:
            target_range = (next_to_process, next_to_process + BITE_SIZE)
        if target_range[1] >= len(self.input) - 1:
            target_range[1] = len(self.input) - 1
            self.last_worker = True
        self.process_range = target_range
        

    def start(self, msg:StartupMsg=None):
        super().start(msg)
        self.initialize()

        if not msg:
            self.set_range()
        else:
            self.creator_id = msg.creator_id
            self.set_range(msg.next_to_process)

        if not self.last_worker:
            
        


if __name__ == "__main__":
    system_input = "000101111000010010000101111000010010"
    print(f"Input length: {len(system_input)}")
    processes = [
        Worker
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