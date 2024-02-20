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


class ProcessFramework(ABC):
    """
    Usage:
        Implemented helpers:
            - get_id -> get process id
            - send_msg -> send msg to process by id
            - new_process -> start new process
            - alive_status -> process still alive

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
            Reason: Simulated server failures can be bypassed this way
    """

    input = None
    output = None
    shared_state = {}

    def __init__(self, id: int):
        self._id: int = id
        self._alive_status: bool = True
        self._alive_status_lock: Lock = Lock()

    @classmethod
    def set_input(cls, input):
        cls.input = input

    def get_id(self) -> int:
        return self._id

    @abstractmethod
    def start(self, msg: str = None):
        raise NotImplementedError()

    @abstractmethod
    def read_msg(self, msg: str):
        raise NotImplementedError()

    def receive_msg(self, msg: str):
        Thread(target=self.read_msg, args=[msg]).start()

    def send_msg(self, target_id: int, msg: str = None):
        if not self.get_alive_status():
            sys.exit()
        if msg and not isinstance(msg, str):
            raise ValueError("Message must be string")
        if DistributedSystem.decide_msg_drop():
            print(f"[STATUS] Dropping message")
            return
        DistributedSystem.msg_to_process(target_id, msg)

    def new_process(self, process_id: int, process_def: type, msg: str = None):
        if not self.get_alive_status():
            sys.exit()
        process_instance = DistributedSystem.initialize_process(process_id, process_def)
        Thread(target=process_instance.start, args=[msg]).start()

    def get_alive_status(self):
        with self._alive_status_lock:
            return self._alive_status

    def complete(self):
        print(f"[STATUS] Process {self.get_id()} complete")
        DistributedSystem.process_completion(self.get_id())

    def shutdown(self, premature=False):
        with self._alive_status_lock:
            self._alive_status = False
        if premature:
            print(f"[STATUS] Process {self.get_id()} experienced hardware failure")
        DistributedSystem.process_shutdown(self.get_id())

class DistributedSystem:
    """
    Usage:
        1. Write process implementations (described above)
        2. Define faults with define_faults call
        3. Call process_input with list of process definitions (not instances) and input
        4. Call wait_for_completion to get output
    """

    _processes: Dict[int, ProcessFramework] = {}
    _processes_lock = Lock()

    _running_process_ids: set = set()
    _running_process_ids_lock = Lock()
    _running_process_ids_cv = Condition(_running_process_ids_lock)

    _msg_drop_prop = 0.0
    _max_process_kill_count = 0
    _process_kill_wait_time = 5

    @classmethod
    def define_faults(
        cls,
        msg_drop_prop: float = 0.0,
        max_process_kill_count: float = 0.0,
        process_kill_wait_time: float = 5,
    ):
        cls._msg_drop_prop = msg_drop_prop
        cls._max_process_kill_count = max_process_kill_count
        cls._process_kill_wait_time = process_kill_wait_time

    @classmethod
    def decide_msg_drop(cls):
        return random.uniform(0.0001, 1) <= cls._msg_drop_prop

    @classmethod
    def shut_down_processes(cls):
        process_kill_count = 0
        while process_kill_count < cls._max_process_kill_count:
            time.sleep(cls._process_kill_wait_time)
            with cls._processes_lock:
                try:
                    process = random.choice(list(cls._processes.values()))
                except IndexError:
                    return
            process.shutdown(premature=True)
            process_kill_count += 1

    @classmethod
    def initialize_process(cls, process_id: int, process_def: type):
        with cls._running_process_ids_lock:
            cls._running_process_ids.add(process_id)
        with cls._processes_lock:
            if process_id in cls._processes:
                print(f"[WARNING] Restarting healthy process {process_id}")
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
                process_id, process_defs[process_id]
            )
            threads.append(Thread(target=process_instance.start))
        for thread in threads:
            thread.start()
        if cls._max_process_kill_count > 0:
            Thread(target=cls.shut_down_processes).start()

    @classmethod
    def msg_to_process(cls, target_id: int, msg: str):
        try:
            with cls._processes_lock:
                cls._processes[target_id].receive_msg(msg)
        except KeyError:
            pass

    @classmethod
    def process_completion(cls, id: int):
        with cls._running_process_ids_lock:
            if id in cls._running_process_ids:
                cls._running_process_ids.remove(id)
            cls._running_process_ids_cv.notify()

    @classmethod
    def process_shutdown(cls, id: int):
        cls.process_completion(id)
        with cls._processes_lock:
            del cls._processes[id]

    @classmethod
    def wait_for_completion(cls):
        with cls._running_process_ids_lock:
            while len(cls._running_process_ids) > 0:
                cls._running_process_ids_cv.wait()
        print("[STATUS] No running processes, initiating shutdown")
        with cls._processes_lock:
            processes: List[ProcessFramework] = list(cls._processes.values())
        for process in processes:
            process.shutdown()
        print("[STATUS] Distributed system shutdown complete")
        return ProcessFramework.output
