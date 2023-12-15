from distributed_systems.base import BaseProcess, DistributedSystem

import time

DONE = "DONE"

class Manager(BaseProcess):
    def start(self):
        BaseProcess.output = 0

        input_len = len(BaseProcess.input)
        middle = int(input_len / 2)
        self.send_msg(0, (0, middle))
        self.send_msg(1, (middle, -1))

        done = 0
        while done < 2:
            if self.read_msg():
                done += 1
            else:
                time.sleep(0.1)
        self.send_msg(2, DONE)
        self.complete()

class Guard(BaseProcess):
    def __init__(self):
        self.owner = None

    def start(self):
        while (True):
            msg = self.read_msg()
            if msg:
                if msg == DONE:
                    break
                else:
                    if not self.owner:
                        
            else:
                time.sleep(0.1)

        self.complete()

class Worker(BaseProcess):
    def start(self):


if __name__ == "__main__":
    processes = [SimpleProcess(0, [0])]
    DistributedSystem.process_input(None, processes)
