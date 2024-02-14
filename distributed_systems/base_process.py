from distributed_systems.framework import ProcessFramework, DistributedSystem

from threading import Lock, Condition, Thread, Event
from queue import Queue
import queue
from enum import Enum
import json
import time
import math

HEARTBEAT_SEND_WAIT_TIME = 1
HEARTBEAT_CHECK_WAIT_TIME = 10


class MsgType(Enum):
    REGULAR = "regular"
    HEARTBEAT = "heartbeat"
    ACKNOWLEDGE = "acknowledge"


class Msg:
    def __init__(
        self,
        src: int = -1,
        msg_type: MsgType = MsgType.REGULAR,
        msg_content: str = None,
        ack_msg: int = -1,
    ):
        self.src: int = src
        self.type: MsgType = msg_type
        self.content: str = msg_content
        self.ack: int = ack_msg

    @staticmethod
    def build_msg(msg_content: str = None):
        return Msg(msg_type=MsgType.REGULAR, msg_content=msg_content, ack_msg=-1)

    def to_json(self):
        self.type = self.type.value
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(json_str: str):
        json_dict = json.loads(json_str)
        return Msg(
            json_dict["src"],
            MsgType(json_dict["type"]),
            json_dict["content"],
            json_dict["ack"],
        )


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

        self._still_processing: bool = True
        self._still_processing_lock: Lock = Lock()

        self._heartbeat_events: dict[int, tuple[Event, bool]] = {}
        self._heartbeat_events_lock: Lock = Lock()

        Thread(target=self._keep_checking_msgs).start()

    def _check_still_processing(self):
        with self._still_processing_lock:
            return self._still_processing

    def read_msg(self, msg: str):
        self.general_inbox.put(Msg.from_json(msg))

    def _acknowledge_msg(self, msg: Msg):
        ack_msg = Msg(
            self.get_id(), msg_type=MsgType.ACKNOWLEDGE, ack_msg=msg.ack
        )
        self.send_msg(msg.src, ack_msg, verify=False)
        unique_msg_id = f"{msg.src}~{msg.ack}"
        with self._processed_msgs_lock:
            if unique_msg_id not in self._processed_msgs:
                self._processed_msgs.add(unique_msg_id)

    def _keep_checking_msgs(self):
        while self._check_still_processing():
            try:
                msg: Msg = self.general_inbox.get(timeout=0.1)
            except queue.Empty:
                continue
            if msg.type == MsgType.ACKNOWLEDGE:
                with self._waiting_acks_lock:
                    self._waiting_acks[msg.ack] = False
                    self._waiting_acks_cv.notify_all()
            elif msg.type == MsgType.HEARTBEAT:
                with self._heartbeat_events_lock:
                    if msg.src in self._heartbeat_events:
                        self._heartbeat_events[msg.src][0].set()
                        if msg.content and msg.content == "FINAL":
                            self._heartbeat_events[msg.src][1] = True
            elif msg.type == MsgType.REGULAR:
                self._acknowledge_msg(msg)
                self.focused_inbox.put(msg)
            else:
                raise ValueError(f"Invalid message type: {msg.type}")

    def _keep_process_alive_continuously(
        self, process_id: int, process_def: type, startup_msg: str = None
    ):
        last_heartbeat_count: int = 0
        with self._heartbeat_events_lock:
            self._heartbeat_events_lock[process_id] = last_heartbeat_count
        while True:
            with self._heartbeat_events_lock:
                try:
                    while self._heartbeat_events_lock[process_id] == last_heartbeat_count:
                        recieved_heartbeat: bool = self._recieved_heartbeats_cv.wait(
                            HEARTBEAT_CHECK_WAIT_TIME
                        )
                        if (
                            math.isinf(self._heartbeat_events_lock[process_id])
                        ):
                            return
                        elif not recieved_heartbeat:
                            self.new_process(process_id, process_def, startup_msg)
                    last_heartbeat_count = self._heartbeat_events_lock[process_id]
                except KeyError:
                    return

    def keep_process_alive(
        self, process_id: int, process_def: type, startup_msg: str = None
    ):
        Thread(
            target=self._keep_process_alive_continuously,
            args=[process_id, process_def, startup_msg],
        ).start()

    def _send_heartbeats_to_process_continuously(self, process_id: int):
        while self._check_still_processing():
            self.send_msg(
                target=process_id, msg=Msg(msg_type=MsgType.HEARTBEAT), verify=False
            )
            time.sleep(HEARTBEAT_SEND_WAIT_TIME)
        self.send_msg(
            target=process_id, msg=Msg(msg_type=MsgType.HEARTBEAT, msg_content="FINAL")
        )

    def send_heartbeats_to_process(self, process_id: int):
        Thread(
            target=self._send_heartbeats_to_process_continuously, args=[process_id]
        ).start()

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
                while self._waiting_acks[msg_id]:
                    success = self._waiting_acks_cv.wait(timeout=retry_time)
                    if not success:
                        super().send_msg(target, msg_string)
        else:
            msg_string = msg.to_json()
            super().send_msg(target, msg_string)

    def complete(self):
        with self._still_processing_lock:
            self._still_processing = False
        super().shutdown()
