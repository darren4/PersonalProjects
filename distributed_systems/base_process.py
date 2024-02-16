from distributed_systems.framework import ProcessFramework, DistributedSystem

from threading import Lock, Condition, Thread, Event
from queue import Queue
import queue
from enum import Enum
import json
import time


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

        self._next_msg_id: int = 0
        self._next_msg_id_lock: Lock = Lock()
        self._ack_events: dict[int, Event] = {}
        self._ack_events_lock: Lock = Lock()

        self._processed_msgs: set[str] = set()
        self._processed_msgs_lock: Lock = Lock()

        self._heartbeat_events: dict[int, Event] = {}
        self._heartbeat_events_lock: Lock = Lock()

        Thread(target=self._keep_checking_msgs).start()

    def read_msg(self, msg: str):
        self.general_inbox.put(Msg.from_json(msg))

    def _acknowledge_msg(self, msg: Msg):
        ack_msg = Msg(self.get_id(), msg_type=MsgType.ACKNOWLEDGE, ack_msg=msg.ack)
        self.send_msg(msg.src, ack_msg, verify=False)
        unique_msg_id = f"{msg.src}~{msg.ack}"
        with self._processed_msgs_lock:
            if unique_msg_id not in self._processed_msgs:
                self._processed_msgs.add(unique_msg_id)

    def _keep_checking_msgs(self):
        while self.get_alive_status():
            try:
                msg: Msg = self.general_inbox.get(timeout=0.1)
            except queue.Empty:
                continue
            if msg.type == MsgType.ACKNOWLEDGE:
                with self._ack_events_lock:
                    if msg.ack in self._ack_events:
                        self._ack_events[msg.ack].set()
            elif msg.type == MsgType.HEARTBEAT:
                with self._heartbeat_events_lock:
                    if msg.src in self._heartbeat_events:
                        self._heartbeat_events[msg.src].set()
            elif msg.type == MsgType.REGULAR:
                self._acknowledge_msg(msg)
                self.focused_inbox.put(msg)
            else:
                raise ValueError(f"Invalid message type: {msg.type}")
        print(f"[DEBUG] process {self.get_id()} stopped sending messages")

    def _keep_process_alive_continuously(
        self,
        process_id: int,
        process_def: type,
        startup_msg: str = None,
        wait_time: float = 5,
    ):
        with self._heartbeat_events_lock:
            process_event = Event()
            self._heartbeat_events[process_id] = process_event
        while self.get_alive_status():
            got_heartbeat = process_event.wait(wait_time)
            if got_heartbeat:
                process_event.clear()
            else:
                if not self.get_alive_status():
                    break
                print(f"[STATUS] Process {self.get_id()} reviving process {process_id}")
                self.new_process(process_id, process_def, startup_msg)
        print(f"[DEBUG] process {self.get_id()} stopped watching process")

    def keep_process_alive(
        self, process_id: int, process_def: type, startup_msg: str = None
    ):
        Thread(
            target=self._keep_process_alive_continuously,
            args=[process_id, process_def, startup_msg],
        ).start()

    def _send_heartbeats_continuously(self, process_id: int, wait_time: float = 1):
        while self.get_alive_status():
            self.send_msg(
                target=process_id, msg=Msg(msg_type=MsgType.HEARTBEAT), verify=False
            )
            time.sleep(wait_time)
        print(f"[DEBUG] process {self.get_id()} stopped sending heartbeats")

    def send_heartbeats_to_process(self, process_id: int):
        Thread(target=self._send_heartbeats_continuously, args=[process_id]).start()

    def get_one_msg(self, timeout=None):
        try:
            return self.focused_inbox.get(timeout=timeout)
        except queue.Empty:
            return None

    def _wait_on_msg_id(self) -> int:
        with self._next_msg_id_lock:
            next_msg_id = self._next_msg_id
            self._next_msg_id += 1
        return next_msg_id

    def send_msg(self, target: int, msg: Msg, verify=True, retry_time: float = 0.1):
        msg.src = self.get_id()
        if verify:
            msg_id = self._wait_on_msg_id()
            msg.ack = msg_id
            msg_string = msg.to_json()
            super().send_msg(target, msg_string)
            with self._ack_events_lock:
                process_event = Event()
                self._ack_events[msg_id] = process_event
            while self.get_alive_status():
                got_ack = process_event.wait(timeout=retry_time)
                if got_ack:
                    with self._ack_events_lock:
                        del self._ack_events[msg_id]
                    return
                else:
                    super().send_msg(target, msg_string)
            if not self.get_alive_status():
                print(f"[DEBUG] process {self.get_id()} stopped checking for message")
        else:
            msg_string = msg.to_json()
            super().send_msg(target, msg_string)

    def complete(self):
        super().shutdown()
