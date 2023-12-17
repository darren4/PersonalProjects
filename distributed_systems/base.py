from distributed_systems import faults

import queue
from abc import ABC, abstractmethod
from typing import List, Dict
from threading import Lock, Thread


"""
Simple User Journey
1. [PROCESS] Determine process connections 
2. [PROCESS] Write process logic
3. [DISTRIBUTE] Add input to shared state
4. [DISTRIBUTE] Start processes in certain order
"""

SRC = "SOURCE"
MSG = "MESSAGE"


class BaseProcess(ABC):
    """
    Rules:
        1. Do not apply thread controls (like threading.Lock) to static variables
        2. Inter-process communication must go through helper functions
    """

    input = None
    output = None
    shared_state = {}

    def __init__(self, id):
        self._id = id
        self._inbox = queue.Queue()

    @classmethod
    def set_input(cls, input):
        cls.input = input

    def get_id(self):
        return self._id

    def receive_msg(self, source_id, msg):
        self._inbox.put({SRC: source_id, MSG: msg})

    def read_msg(self):
        try:
            return self._inbox.get()
        except queue.Empty:
            return None

    def send_msg(self, target_id, msg):
        DistributedSystem.msg_to_process(self.get_id(), target_id, msg)

    @abstractmethod
    def start(self):
        raise NotImplementedError()

    def complete(self):
        print(f"Process {self.get_id()} complete")
        DistributedSystem.end_process(self.get_id())


class DistributedSystem:
    _processes : Dict[int, BaseProcess] = {}
    _processes_lock = Lock()

    @classmethod
    def process_input(cls, input, processes: List[BaseProcess]):
        BaseProcess.set_input(input)
        with cls._processes_lock:
            threads : List[Thread] = []
            for process in processes:
                cls._processes[process.get_id()] = process
                threads.append(Thread(target=process.start))
            for thread in threads:
                thread.start()

    @classmethod
    def msg_to_process(cls, source_id, target_id, msg):
        if faults.message_not_sent():
            return
        try:
            with cls._processes_lock:
                cls._processes[target_id].receive_msg(source_id, msg)
        except KeyError:
            raise ValueError(f"process {target_id} does not exist")

    @classmethod
    def end_process(cls, id):
        with cls._processes_lock:
            del cls._processes[id]
