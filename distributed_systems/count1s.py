from distributed_systems.framework import BaseProcess, DistributedSystem, SRC, MSG

import time
from threading import Lock, Condition, Thread
from queue import Queue
from enum import Enum
from typing import Dict, Set
from abc import abstractmethod


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
    def __init__(self, msg_type: MsgType=MsgType.REG, msg_content=None, ack_msg: int=-1):
        self.type: MsgType = msg_type
        self.content = msg_content
        self.ack: int = ack_msg

class Process(BaseProcess):
    def initialize(self):
        self.general_inbox: Queue[Dict] = Queue()
        self.focused_inbox: Queue[Dict] = Queue()

        self._waiting_acks: Dict[int, bool] = {}
        self._waiting_acks_lock: Lock = Lock()
        self._waiting_acks_cv: Condition = Condition(self._waiting_acks_lock)

        self._processed_msgs: Set[str] = set()
        self._processed_msgs_lock: Lock = Lock()

        self._done_processing: bool = False
        self._done_processing_lock: Lock = Lock()

        Thread(target=self._keep_checking_msgs).start()

    def read_msg(self, source_id: int, msg: Msg):
        self.general_inbox.put({SRC: source_id, MSG: msg})

    def _keep_checking_msgs(self):
        while True:
            if self.check_done_processing():
                self.complete()
                return
            src_and_msg = self.general_inbox.get()
            source = src_and_msg[SRC]
            msg: Msg = src_and_msg[MSG]
            if msg.type == MsgType.ACK:
                with self._waiting_acks_lock:
                    self._waiting_acks[msg.ack] = False
                    self._waiting_acks_cv.notify_all()
            elif msg.type == MsgType.REG:
                ack_msg = Msg(msg_type=MsgType.ACK, ack_msg=msg.ack)
                self.send_msg(source, ack_msg)
                unique_msg_id = f"{source}~{msg.ack}"
                needs_processing = False
                with self._processed_msgs_lock:
                    if unique_msg_id not in self._processed_msgs:
                        self._processed_msgs.add(unique_msg_id)
                        needs_processing = True
                if needs_processing:
                    self.focused_inbox.put(src_and_msg)
            else:
                print(f"[DEBUG] Unrecognized message type: {msg.type}")
                assert False

    def get_one_msg(self):
        return self.focused_inbox.get()

    def _wait_on_msg_id(self) -> int:
        with self._waiting_acks_lock:
            msg_id = len(self._waiting_acks)
            self._waiting_acks[msg_id] = True
            return msg_id

    def send_msg_verify(self, target: int, msg: Msg, retry_time: float=0.1):
        msg_id = self._wait_on_msg_id()
        msg.ack = msg_id
        self.send_msg(target, msg)

        with self._waiting_acks_lock:
            while self._waiting_acks[msg_id]:
                success = self._waiting_acks_cv.wait(timeout=retry_time)
                if not success:
                    self.send_msg(target, msg)

    def set_done_processing(self):
        with self._done_processing_lock:
            self._done_processing = True

    def check_done_processing(self) -> bool:
        with self._done_processing_lock:
            return self._done_processing

class Manager(Process):
    def start(self):
        BaseProcess.output = 0
        bite_size = 5
        input_len = len(BaseProcess.input)
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
    def __init__(self, id):
        super().__init__(id)
        self.owner = None

    def start(self):
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
        input_window = BaseProcess.input[bounds[0] : bounds[1]]
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
        BaseProcess.output += one_count
        self.send_msg(GUARD_ID, Msg())

    def start(self):
        while True:
            self.send_msg_verify(MANAGER_ID, Msg())
            msg = self.get_one_msg()
            if msg[MSG].content == DONE:
                self.set_done_processing()
                return
            elif type(msg[MSG].content) == tuple:
                self._process_window(msg[MSG].content)
            else:
                print(f"[DEBUG] Unrecognized message: {msg[MSG].content}")


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
