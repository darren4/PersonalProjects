from distributed_systems.framework import ProcessFramework, DistributedSystem, SRC, MSG

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
        self, msg_type: MsgType = MsgType.REG, msg_content=None, ack_msg: int = -1
    ):
        self.type: MsgType = msg_type
        self.content = msg_content
        self.ack: int = ack_msg


class Process(ProcessFramework):
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
            try:
                src_and_msg = self.general_inbox.get(timeout=0.1)
            except queue.Empty:
                if self.check_done_processing():
                    self.complete()
                    return
                else:
                    continue
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

    def send_msg_verify(self, target: int, msg: Msg, retry_time: float = 0.1):
        msg_id = self._wait_on_msg_id()
        msg.ack = msg_id
        self.send_msg(target, msg)

        with self._waiting_acks_lock:
            while self._waiting_acks[msg_id]:
                success = self._waiting_acks_cv.wait(timeout=retry_time)
                if not success:
                    try:
                        self.send_msg(target, msg)
                    except DistributedSystem.NonExistentProcess as e:
                        assert e.process == target
                        return

    def set_done_processing(self):
        with self._done_processing_lock:
            self._done_processing = True

    def check_done_processing(self) -> bool:
        with self._done_processing_lock:
            return self._done_processing
