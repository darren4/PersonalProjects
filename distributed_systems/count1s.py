from distributed_systems.framework import BaseProcess, DistributedSystem, SRC, MSG

import time
from threading import Event, Lock, Condition
from queue import Queue
from enum import Enum
from typing import List


DONE = "DONE"

MANAGER_ID = 0
GUARD_ID = 1
WORKER_0_ID = 2
WORKER_1_ID = 3

WORKER_COUNT = 2

class MsgType(Enum):
    ACK = 1
    REG = 2

class Msg:
    def __init__(self, msg_type: MsgType=MsgType.REG, msg_content=None):
        self.type: MsgType = msg_type
        self.content = msg_content

class Process(BaseProcess):
    def initialize(self):
        self.inbox: Queue = Queue()

        self._waiting_acks: List[bool] = []
        self._waiting_acks_lock: Lock = Lock()
        self._waiting_acks_cv: Condition = Condition(self._waiting_acks_lock)

        self._free_ack_ids: set = set()
        self._free_ack_ids_lock: Lock = Lock()

        self._done_processing: bool = False
        self._done_processing_lock: Lock = Lock()

    def read_msg(self, source_id, msg):
        self.inbox.put({SRC: source_id, MSG: msg})

    def _set_done_processing(self):
        with self._done_processing_lock:
            self._done_processing = True

    def _check_done_processing(self):
        with self._done_processing_lock:
            return self._done_processing

    def _keep_checking_msgs(self):
        while True:
            if self._check_done_processing():
                return
            src_and_msg = self.inbox.get()
            source = src_and_msg[SRC]
            msg: Msg = src_and_msg[MSG]
            if msg.type == MsgType.ACK:
                with self._waiting_acks_lock:
                    self._

    def _wait_on_msg_id(self):
        with self._free_ack_ids_lock:
            if self._free_ack_ids:
                return self._free_ack_ids.pop()
        with self._waiting_acks_lock:
            msg_id = len(self._waiting_acks)
            self._waiting_acks.append(True)
            return msg_id

    def send_msg_verify(self, target, msg, retry_time=0.1):
        msg_id = self._wait_on_msg_id()
        self.send_msg(target, msg)

        with self._waiting_acks_lock:
            while self._waiting_acks[msg_id]:
                success = self._waiting_acks_cv.wait(timeout=retry_time)
                if not success:
                    self.send_msg(target, msg)

class Manager(Process):
    def start(self):
        BaseProcess.output = 0
        bite_size = 5
        input_len = len(BaseProcess.input)
        for window_start in range(0, input_len, bite_size):
            window_end = min(window_start + bite_size, input_len)
            msg = self.get_one_msg()
            self.send_msg(msg[SRC], (window_start, window_end))
        for _ in range(WORKER_COUNT):
            msg = self.get_one_msg()
            self.send_msg(msg[SRC], DONE)
        self.send_msg(GUARD_ID, DONE)
        self.complete()


class Guard(Process):
    def __init__(self, id):
        super().__init__(id)
        self.owner = None

    def start(self):
        while True:
            msg = self.get_one_msg()
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
        input_window = BaseProcess.input[bounds[0] : bounds[1]]
        one_count = 0
        for char in input_window:
            if char == "1":
                one_count += 1

        holding_lock = False
        while not holding_lock:
            self.send_msg(GUARD_ID)
            msg = self.get_one_msg()
            assert msg[SRC] == GUARD_ID
            holding_lock = msg[MSG]
        BaseProcess.output += one_count
        self.send_msg(GUARD_ID)

    def start(self):
        while True:
            self.send_msg(MANAGER_ID)
            msg = self.get_one_msg()
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
