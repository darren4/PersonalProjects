import sys
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Type
from threading import Lock, Thread, Condition
import random


"""
Simple User Journey
1. [PROCESS] Determine process connections 
2. [PROCESS] Write process logic
3. [DISTRIBUTE] Add input to shared state
4. [DISTRIBUTE] Start processes in certain order
"""

MESSAGE_FAULTS_ENABLED = True
PROCESS_FAULTS_ENABLED = True


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

    def __init__(self, id):
        self._id = id
        self._alive_status = True
        self._alive_status_lock = Lock()

    @classmethod
    def set_input(cls, input):
        cls.input = input

    def get_id(self):
        return self._id

    @abstractmethod
    def start(self, msg=None):
        raise NotImplementedError()

    @abstractmethod
    def read_msg(self, msg):
        raise NotImplementedError()

    def receive_msg(self, msg):
        Thread(target=self.read_msg, args=[msg]).start()

    def send_msg(self, target_id, msg=None):
        if MESSAGE_FAULTS_ENABLED and random.randint(0, 10) == 0:
            # Hardware Failure
            return
        if not self.get_alive_status():
            sys.exit()
        DistributedSystem.msg_to_process(target_id, msg)

    def new_process(self, process_def: Type, process_id: int, msg=None):
        process_instance = DistributedSystem.initialize_process(process_def, process_id)
        Thread(target=process_instance.start, args=[msg]).start()

    def get_alive_status(self):
        with self._alive_status_lock:
            return self._alive_status

    def complete(self, success=True):
        if not self.get_alive_status():
            return
        with self._alive_status_lock:
            self._alive_status = False
        if success:
            print(f"[STATUS] Process {self.get_id()} completed successfully")
        else:
            print(f"[STATUS] Process {self.get_id()} experienced hardware failure")
        DistributedSystem.end_process(self.get_id())


class DistributedSystem:
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
    def initialize_process(cls, process_def: Type, process_id: int):
        if not PROCESS_FAULTS_ENABLED:
            return
        with cls._processes_lock:
            if process_id in cls._processes:
                raise ValueError(f"Process already holding id {process_id}")
            process_instance: ProcessFramework = process_def(process_id)
            print(f"[STATUS] Starting process {process_id}")
            cls._processes[process_instance.get_id()] = process_instance
            return process_instance

    @classmethod
    def process_input(cls, input, process_defs: List[Type]):
        ProcessFramework.set_input(input)
        threads: List[Thread] = []
        for process_id in range(len(process_defs)):
            process_instance = cls.initialize_process(
                process_defs[process_id], process_id
            )
            threads.append(Thread(target=process_instance.start))
        for thread in threads:
            thread.start()
        Thread(target=cls.shut_down_processes).start()

    @classmethod
    def msg_to_process(cls, target_id, msg):
        try:
            with cls._processes_lock:
                cls._processes[target_id].receive_msg(msg)
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
        print("[STATUS] No remaining running processes")
        return ProcessFramework.output
