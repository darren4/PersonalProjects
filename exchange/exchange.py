from queue import PriorityQueue
from queue import Empty

PARTICIPANT_ID = "PARTICIPANT_ID"
ACTION = "ACTION"
BUY = "BUY"
SELL = "SELL"
PRICE = "PRICE"
AMOUNT = "AMOUNT"

ORDER = "ORDER"
MATCH = "MATCH"

class Exchange:

    def __init__(self):
        self._buy_order_queue = PriorityQueue()
        self._sell_order_queue = PriorityQueue()
        self.tape = []

    def trade(self, participant_id, action, price: float, amount: int):
        order = {
            PARTICIPANT_ID: participant_id,
            ACTION: action,
            PRICE: price,
            AMOUNT: amount
        }
        if action == BUY:
            self._buy_order_queue.put((-price, order))
        elif action == SELL:
            self._sell_order_queue.put((price, order))
        else:
            raise ValueError("action must be BUY or SELL")
        self.tape.append((ORDER, order))

    def _try_match_trade(self) -> bool:
        try:
            largest_buy = self._buy_order_queue.get()[1]
            largest_sell = self._sell_order_queue.get()[1]
        except Empty:
            return False
        
        

    