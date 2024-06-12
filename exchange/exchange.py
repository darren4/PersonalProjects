from queue import PriorityQueue
from queue import Empty
from dataclasses import dataclass
from enum import Enum
from typing import Tuple, List, Union


@dataclass
class Holdings:
    cash: float
    security: float


class Action(Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class Order:
    participant: int
    action: Action
    price: float
    amount: int


class OrderQueue:
    def __init__(self, max_has_priority: bool):
        self._order_queue: PriorityQueue[Tuple[int, Order]] = PriorityQueue()
        if max_has_priority:
            self._multiplier = -1
        else:
            self._multiplier = 1

    def put(self, order: Order) -> None:
        self._order_queue.put((self._multiplier * order.price, order))

    def get(self, timeout: Union[int, float, None] = None) -> Order:
        return self._order_queue.get(timeout=timeout)[1]


class SingleSecurityExchange:
    def __init__(self, participants: List[Holdings]):
        self._buy_order_queue: OrderQueue = OrderQueue(True)
        self._sell_order_queue: OrderQueue = OrderQueue(False)
        self.tape: List[Order] = []

        self._participants: List[Holdings] = participants

    def trade(self, order: Order):
        if order.action == Action.BUY:
            if order.amount * order.price > self._participants[order.participant].cash:
                raise ValueError("insufficient funds")
            self._buy_order_queue.put(order)
        elif order.action == Action.SELL:
            if order.amount > self._participants[order.participant].security:
                raise ValueError("insufficient security holdings")
            self._sell_order_queue.put(order)
        else:
            raise ValueError("action must be BUY or SELL")
        self.tape.append(order)

    def try_match_trade(self) -> bool:
        buy_order: Order = self._buy_order_queue.get()
        sell_order: Order = self._sell_order_queue.get()

        if buy_order.price <= sell_order.price:
            self._buy_order_queue.put(buy_order)
            self._sell_order_queue.put(sell_order)
            return False

        amount_moved: int = min(sell_order.amount, buy_order.amount)
        self._participants[buy_order.participant].cash -= amount_moved * buy_order.price
        self._participants[buy_order.participant].security += amount_moved
        self._participants[sell_order.participant].cash += (
            amount_moved * sell_order.price
        )
        self._participants[sell_order.participant].security -= amount_moved

        if amount_moved < sell_order.amount:
            self._sell_order_queue.put(
                Order(
                    sell_order.participant,
                    sell_order.action,
                    sell_order.price,
                    sell_order.amount - amount_moved,
                )
            )
        elif amount_moved < buy_order.amount:
            self._buy_order_queue.put(
                Order(
                    buy_order.participant,
                    buy_order.action,
                    buy_order.price,
                    buy_order.amount - amount_moved,
                )
            )
        return True


class BaseParticipant:
    pass
