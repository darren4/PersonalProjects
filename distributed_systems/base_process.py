from distributed_systems.framework import ProcessFramework, DistributedSystem

from threading import Lock, Condition, Thread
from queue import Queue
import queue
from enum import Enum
from typing import Dict, Set


class MsgType(Enum):
    ACK = 1
    REG = 2


class Msg:
    def __init__(
        self, src: int, msg_type: MsgType = MsgType.REG, msg_content=None, ack_msg: int = -1
    ):
        self.src = src
        self.type: MsgType = msg_type
        self.content = msg_content
        self.ack: int = ack_msg


class Process(ProcessFramework):
    def start(self, msg=None):
        """
        Call in first line of start in inherited class
        """
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

    def read_msg(self, msg: Msg):
        self.general_inbox.put(msg)

    def _keep_checking_msgs(self):
        while True:
            try:
                msg: Msg = self.general_inbox.get(timeout=0.1)
            except queue.Empty:
                if self.check_done_processing():
                    self.complete()
                    return
                else:
                    continue
            if msg.type == MsgType.ACK:
                with self._waiting_acks_lock:
                    self._waiting_acks[msg.ack] = False
                    self._waiting_acks_cv.notify_all()
            elif msg.type == MsgType.REG:
                ack_msg = Msg(self.get_id(), msg_type=MsgType.ACK, ack_msg=msg.ack)
                self.send_msg(msg.src, ack_msg)
                unique_msg_id = f"{msg.src}~{msg.ack}"
                with self._processed_msgs_lock:
                    if unique_msg_id not in self._processed_msgs:
                        self._processed_msgs.add(unique_msg_id)
                        self.focused_inbox.put(msg)
            else:
                print(f"[DEBUG] Unrecognized message type: {msg.type}")
                assert False

    def get_one_msg(self, timeout=None):
        try:
            return self.focused_inbox.get(timeout=timeout)
        except queue.Empty:
            return None

    def _wait_on_msg_id(self) -> int:
        with self._waiting_acks_lock:
            msg_id = len(self._waiting_acks)
            self._waiting_acks[msg_id] = True
            return msg_id

    def send_msg_verify(self, target: int, msg: Msg, retry_time: float = 0.1):
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
