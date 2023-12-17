from distributed_systems.base import BaseProcess, DistributedSystem, SRC, MSG

import time

DONE = "DONE"

MANAGER_ID = 0
GUARD_ID = 1
WORKER_0_ID = 2
WORKER_1_ID = 3


class Manager(BaseProcess):
    def start(self):
        BaseProcess.output = 0

        input_len = len(BaseProcess.input)
        middle = int(input_len / 2)
        self.send_msg(WORKER_0_ID, (0, middle))
        self.send_msg(WORKER_1_ID, (middle, -1))

        done = 0
        while done < 2:
            if self.read_msg():
                done += 1
            else:
                time.sleep(0.1)
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
                if msg[MSG] == DONE:
                    break
                else:
                    if not self.owner:
                        self.send_msg(int(msg[MSG]), True)
                        self.owner = int(msg[MSG])
                    elif self.owner == int(msg[MSG]):
                        self.owner = None
                    else:
                        self.send_msg(int(msg[MSG]), False)
            else:
                time.sleep(0.1)
        self.complete()


class Worker(BaseProcess):
    def start(self):
        msg = None
        while not msg:
            msg = self.read_msg()
            time.sleep(0.1)
        assert msg[SRC] == MANAGER_ID
        if msg[MSG][1] == -1:
            input_portion = BaseProcess.input[msg[MSG][0] :]
        else:
            input_portion = BaseProcess.input[msg[MSG][0] : msg[MSG][1]]
        one_count = 0
        for char in input_portion:
            if int(char) == 1:
                one_count += 1

        gained_access = False
        while not gained_access:
            self.send_msg(GUARD_ID, self.get_id())
            msg = None
            while not msg:
                msg = self.read_msg()
                time.sleep(0.1)
            assert msg[SRC] == GUARD_ID
            if msg[MSG]:
                gained_access = True
            else:
                time.sleep(0.1)

        BaseProcess.output += one_count
        self.send_msg(GUARD_ID, self.get_id())
        self.send_msg(MANAGER_ID, DONE)
        self.complete()


if __name__ == "__main__":
    system_input = "000101111000010010000101111000010010"
    processes = [
        Manager(MANAGER_ID),
        Guard(GUARD_ID),
        Worker(WORKER_0_ID),
        Worker(WORKER_1_ID),
    ]
    DistributedSystem.process_input(system_input, processes)
    time.sleep(2)
    assert BaseProcess.output == 14
