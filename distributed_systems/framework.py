import sys
import time
from abc import ABC, abstractmethod
from threading import Lock, Thread, Condition
import random
from typing import List, Dict


"""
Simple User Journey
1. [PROCESS] Determine process connections 
2. [PROCESS] Write process logic
3. [DISTRIBUTE] Add input to shared state
4. [DISTRIBUTE] Start processes in certain order
"""

MESSAGE_FAULTS_ENABLED = True
PROCESS_FAULTS_ENABLED = False


class ProcessFramework(ABC):
    """
    Usage:
        Implemented helpers:
            - get_id -> get process id
            - send_msg -> send msg to process by id

        Mandatory implement:
            - read_msg -> process message
            - start -> start process execution

        Other:
            - complete -> call when process done

    Rules:
        1. Do not apply thread controls (like threading.Lock) to static variables
            Reason: These only work on single machines, not distributed systems
        2. Inter-process communication must go through functions read_msg and send_msg
            Reason: Simulated message dropping can be bypassed this way
        3. Do not catch SystemExit exceptions
            Reason: Simulated hardware failures can be bypassed this way
    """

    input = None
    output = None
    shared_state = {}

    def __init__(self, id: int):
        self._id: int = id
        self._alive_status: bool = True
        self._alive_status_lock: Lock = Lock()
        self._processing_status: bool = True
        self._processing_status_lock: Lock = Lock()

    @classmethod
    def set_input(cls, input):
        cls.input = input

    def get_id(self) -> int:
        return self._id

    @abstractmethod
    def start(self, msg: str=None):
        raise NotImplementedError()

    @abstractmethod
    def read_msg(self, msg: str):
        raise NotImplementedError()

    def receive_msg(self, msg: str):
        Thread(target=self.read_msg, args=[msg]).start()

    def send_msg(self, target_id: int, msg: str=None):
        if not self.get_alive_status():
            sys.exit()
        if msg and not isinstance(msg, str):
            raise ValueError("Message must be string")
        if MESSAGE_FAULTS_ENABLED and random.randint(0, 5) == 0:
            # Hardware Failure
            return
        DistributedSystem.msg_to_process(target_id, msg)

    def new_process(self, process_def: type, process_id: int, msg: str=None):
        process_instance = DistributedSystem.initialize_process(process_def, process_id)
        Thread(target=process_instance.start, args=[msg]).start()

    def get_processing_status(self):
        with self._processing_status_lock:
            return self._processing_status

    def get_alive_status(self):
        with self._alive_status_lock:
            return self._alive_status

    def notify_done_processing(self):
        with self._processing_status_lock:
            self._processing_status = False
        DistributedSystem.process_done()

    def complete(self):
        if not self.get_alive_status():
            return
        self.notify_done_processing()
        print(f"[STATUS] Process {self.get_id()} done processing")

    def force_kill(self):
        with self._alive_status_lock:
            self._alive_status = False
        print(f"[STATUS] Process {self.get_id()} shut down")
        self.notify_done_processing()
        DistributedSystem.remove_process(self.get_id())

class DistributedSystem:
    _processing_count: int = 0
    _processes: Dict[int, ProcessFramework] = {}
    _processes_lock = Lock()
    _processes_cv = Condition(_processes_lock)

    @classmethod
    def shut_down_processes(cls):
        # Hardware Failure
        time.sleep(5)
        with cls._processes_lock:
            try:
                process = random.choice(list(cls._processes.values()))
            except IndexError:
                return
        process.complete(False)

    @classmethod
    def initialize_process(cls, process_def: type, process_id: int):
        with cls._processes_lock:
            if process_id in cls._processes:
                raise ValueError(f"Process already holding id {process_id}")
            cls._processing_count += 1
            process_instance: ProcessFramework = process_def(process_id)
            print(f"[STATUS] Starting process {process_id}")
            cls._processes[process_instance.get_id()] = process_instance
            return process_instance

    @classmethod
    def process_input(cls, input, process_defs: List[type]):
        ProcessFramework.set_input(input)
        threads: list[Thread] = []
        for process_id in range(len(process_defs)):
            process_instance = cls.initialize_process(
                process_defs[process_id], process_id
            )
            threads.append(Thread(target=process_instance.start))
        for thread in threads:
            thread.start()
        # Thread(target=cls.shut_down_processes).start()

    @classmethod
    def msg_to_process(cls, target_id: int, msg: str):
        try:
            with cls._processes_lock:
                cls._processes[target_id].receive_msg(msg)
        except KeyError:
            pass

    @classmethod
    def process_done(cls):
        with cls._processes_lock:
            cls._processing_count -= 1
            cls._processes_cv.notify()

    @classmethod
    def remove_process(cls, id: int):
        with cls._processes_lock:
            del cls._processes[id]

    @classmethod
    def wait_for_completion(cls):
        with cls._processes_lock:
            while cls._processing_count:
                cls._processes_cv.wait()
            process_ids = list(cls._processes.keys())
            for process_id in process_ids:
                process: ProcessFramework = cls._processes[process_id]
                process._alive_status = False
                del cls._processes[process_id]
        print("[STATUS] No remaining running processes")
        return ProcessFramework.output
