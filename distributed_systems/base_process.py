from distributed_systems.framework import ProcessFramework, DistributedSystem

from threading import Lock, Condition, Thread
from queue import Queue
import queue
from enum import StrEnum
import json


class MsgType(StrEnum):
    REGULAR = "regular"
    HEARTBEAT = "heartbeat"
    ACKNOWLEDGE = "acknowledge"


class Msg:
    def __init__(
        self,
        src: int=-1,
        msg_type: MsgType=MsgType.REGULAR,
        msg_content: str=None,
        ack_msg: int = -1,
    ):
        self.src: int = src
        self.type: str = msg_type
        self.content: str = msg_content
        self.ack: int = ack_msg

    @staticmethod
    def build_msg(msg_content: str=None):
        return Msg(msg_type=MsgType.REGULAR, msg_content=msg_content, ack_msg=-1)

    def to_json(self):
        return json.dumps(self.__dict__)
    
    @staticmethod
    def from_json(json_str: str):
        json_dict = json.loads(json_str)
        return Msg(json_dict.src, MsgType(json_dict.msg_type), json_dict.msg_content, json_dict.ack_msg)


class Process(ProcessFramework):
    def start(self, msg: str=None):
        """
        Call in first line of start in inherited class
        """
        self.general_inbox: Queue[Msg] = Queue()
        self.focused_inbox: Queue[Msg] = Queue()

        self._waiting_acks: dict[int, bool] = {}
        self._waiting_acks_lock: Lock = Lock()
        self._waiting_acks_cv: Condition = Condition(self._waiting_acks_lock)

        self._processed_msgs: set[str] = set()
        self._processed_msgs_lock: Lock = Lock()

        self._done_processing: bool = False
        self._done_processing_lock: Lock = Lock()

        Thread(target=self._keep_checking_msgs).start()

    def read_msg(self, msg: str):
        self.general_inbox.put(Msg.from_json(msg))

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
            if msg.type == MsgType.ACKNOWLEDGE:
                with self._waiting_acks_lock:
                    self._waiting_acks[msg.ack] = False
                    self._waiting_acks_cv.notify_all()
            elif msg.type == MsgType.HEARTBEAT:
                self.focused_inbox.put(msg)
            elif msg.type == MsgType.REGULAR:
                ack_msg = Msg(self.get_id(), msg_type=MsgType.ACKNOWLEDGE, ack_msg=msg.ack)
                self.send_msg(msg.src, ack_msg)
                unique_msg_id = f"{msg.src}~{msg.ack}"
                with self._processed_msgs_lock:
                    if unique_msg_id not in self._processed_msgs:
                        self._processed_msgs.add(unique_msg_id)
                        self.focused_inbox.put(msg)
            else:
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

    def send_msg(self, target: int, msg: Msg, verify=True, retry_time: float = 0.1):
        msg.src = self.get_id()
        msg_string = msg.to_json()
        if verify:
            msg_id = self._wait_on_msg_id()
            msg.ack = msg_id
            super().send_msg(target, msg_string)
            with self._waiting_acks_lock:
                while self._waiting_acks[msg_id] and not self.check_done_processing():
                    success = self._waiting_acks_cv.wait(timeout=retry_time)
                    if not success:
                        super().send_msg(target, msg_string)
        else:
            super().send_msg(target, msg_string)

    def set_done_processing(self):
        with self._done_processing_lock:
            self._done_processing = True

    def check_done_processing(self) -> bool:
        with self._done_processing_lock:
            return self._done_processing or not self.get_alive_status()
