import queue
from abc import ABC, abstractmethod
from typing import List

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
    input = None
    shared_state = {}

    def __init__(self, id, connecting_ids):
        self._id = id
        self._connecting_ids = connecting_ids
        self._inbox = queue.Queue()

    @classmethod
    def set_input(cls, input):
        cls.input = input

    def get_id(self):
        return self._id
    
    def receive_msg(self, source_id, msg):
        self._inbox.put({
            SRC: source_id,
            MSG: msg
        })

    def read_msg(self):
        return self._inbox.get()

    def send_msg(self, target_id, msg):
        DistributedSystem.msg_to_process(self.get_id(), target_id, msg)

    @abstractmethod
    def start(self):
        raise NotImplementedError()
    
    def complete(self):
        print(f"Process {self.get_id()} complete")
        DistributedSystem.end_process(self.get_id())

class DistributedSystem:
    _processes = {}

    @classmethod
    def process_input(cls, input, processes: List[BaseProcess]):
        for process in processes:
            cls._processes[process.get_id()] = process

        BaseProcess.set_input(input)
        for process in processes:
            process.start()

    @classmethod
    def msg_to_process(cls, source_id, target_id, msg):
        try:
            cls._processes[target_id].receive_msg(source_id, msg)
        except KeyError:
            raise ValueError(f"process {target_id} does not exist")

    @classmethod
    def end_process(cls, id):
        del cls._processes[id]

