from distributed_systems.framework import ProcessFramework, DistributedSystem

from threading import Lock, Condition, Thread
from queue import Queue
import queue
from enum import Enum
import json


class MsgType(Enum):
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
        self.type = self.type.value
        return json.dumps(self.__dict__)
    
    @staticmethod
    def from_json(json_str: str):
        json_dict = json.loads(json_str)
        return Msg(json_dict["src"], MsgType(json_dict["type"]), json_dict["content"], json_dict["ack"])


class Process(ProcessFramework):
    def start_background_processing(self):
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
        while self.get_alive_status():
            try:
                msg: Msg = self.general_inbox.get(timeout=0.1)
            except queue.Empty:
                continue

            if msg.type == MsgType.ACKNOWLEDGE:
                with self._waiting_acks_lock:
                    self._waiting_acks[msg.ack] = False
                    self._waiting_acks_cv.notify_all()
            elif msg.type == MsgType.HEARTBEAT:
                self.focused_inbox.put(msg)
            elif msg.type == MsgType.REGULAR:
                ack_msg = Msg(self.get_id(), msg_type=MsgType.ACKNOWLEDGE, ack_msg=msg.ack)
                self.send_msg(msg.src, ack_msg, verify=False)
                unique_msg_id = f"{msg.src}~{msg.ack}"
                with self._processed_msgs_lock:
                    if unique_msg_id not in self._processed_msgs:
                        self._processed_msgs.add(unique_msg_id)
                        self.focused_inbox.put(msg)
            else:
                raise ValueError(f"Invalid message type: {msg.type}")
            
    def keep_process_alive(self, process_id, startup_msg: str=None):
        pass

    def send_heartbeats_to_process(self, process_id):
        pass

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
        if verify:
            msg_id = self._wait_on_msg_id()
            msg.ack = msg_id
            msg_string = msg.to_json()
            super().send_msg(target, msg_string)
            with self._waiting_acks_lock:
                while self._waiting_acks[msg_id] and self.get_alive_status():
                    success = self._waiting_acks_cv.wait(timeout=retry_time)
                    if not success:
                        super().send_msg(target, msg_string)
        else:
            msg_string = msg.to_json()
            super().send_msg(target, msg_string)
