from distributed_systems import faults

import sys
import time
from abc import ABC, abstractmethod
from typing import List, Dict
from threading import Lock, Thread, Condition
import random


"""
Simple User Journey
1. [PROCESS] Determine process connections 
2. [PROCESS] Write process logic
3. [DISTRIBUTE] Add input to shared state
4. [DISTRIBUTE] Start processes in certain order
"""

SRC = "SOURCE"
MSG = "MESSAGE"


class ProcessFramework(ABC):
    """
    Rules:
        1. Do not apply thread controls (like threading.Lock) to static variables
            Reason: These only work on single machines, not distributed systems
        2. Inter-process communication must go through the helper functions read_msg and send_msg
            Reason: Simulated message dropping can be bypassed this way
        3. Do not catch SystemExit exceptions
            Reason: Simulated hardware failures can be bypassed this way
    """

    input = None
    output = None
    shared_state = {}

    def __init__(self, id):
        self._id = id
        self._alive = True
        self._alive_lock = Lock()
        self.initialize()

    def initialize(self):
        """
        Effectively process constructor. Optional to implement.
        """
        pass

    def force_shutdown(self):
        with self._alive_lock:
            self._alive = False
        self.complete(success=False)

    def still_alive(self):
        with self._alive_lock:
            return self._alive

    @classmethod
    def set_input(cls, input):
        cls.input = input

    def get_id(self):
        return self._id

    @abstractmethod
    def read_msg(self, source_id, msg):
        raise NotImplementedError()

    def receive_msg(self, source_id, msg):
        Thread(target=self.read_msg, args=[source_id, msg]).start()

    def send_msg(self, target_id, msg=None):
        if faults.message_not_sent():
            return
        if not self.still_alive():
            sys.exit()
        DistributedSystem.msg_to_process(self.get_id(), target_id, msg)

    @abstractmethod
    def start(self):
        raise NotImplementedError()

    def complete(self, success=True):
        if success:
            print(f"Process {self.get_id()} completed successfully")
        else:
            print(f"Process {self.get_id()} suffered an unplanned shutdown")
        DistributedSystem.end_process(self.get_id())


class DistributedSystem:
    _processes: Dict[int, ProcessFramework] = {}
    _processes_lock = Lock()
    _processes_cv = Condition(_processes_lock)

    @classmethod
    def shut_down_processes(cls):
        while cls.some_processes_alive():
            time.sleep(faults.PROCESS_KILL_WAIT)
            with cls._processes_lock:
                random.choice(list(cls._processes.values())).force_shutdown()

    @classmethod
    def process_input(cls, input, processes: List[ProcessFramework]):
        ProcessFramework.set_input(input)
        with cls._processes_lock:
            threads: List[Thread] = []
            for process in processes:
                cls._processes[process.get_id()] = process
                threads.append(Thread(target=process.start))
            for thread in threads:
                thread.start()
        if faults.FAULTS_ENABLED:
            Thread(target=cls.shut_down_processes).start()

    @classmethod
    def msg_to_process(cls, source_id, target_id, msg):
        try:
            with cls._processes_lock:
                cls._processes[target_id].receive_msg(source_id, msg)
        except KeyError:
            pass

    @classmethod
    def end_process(cls, id):
        with cls._processes_lock:
            del cls._processes[id]
            cls._processes_cv.notify()

    @classmethod
    def some_processes_alive(cls):
        with cls._processes_lock:
            return bool(cls._processes)

    @classmethod
    def wait_for_completion(cls):
        with cls._processes_lock:
            while cls._processes:
                cls._processes_cv.wait()
        print("Distributed system completed successfully")
        return ProcessFramework.output
