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

CASH = "CASH"
SECURITY = "SECURITY"


class Exchange:
    def __init__(self, participants):
        """
        participants: dictionary of participant_id (key) to dictionary of cash/security amount (value)
        """
        self._buy_order_queue = PriorityQueue()
        self._sell_order_queue = PriorityQueue()
        self.tape = []

        self._participants = participants

    def trade(self, participant_id: int, action: str, price: float, amount: int):
        order = {
            PARTICIPANT_ID: participant_id,
            ACTION: action,
            PRICE: price,
            AMOUNT: amount,
        }
        if action == BUY:
            if order[AMOUNT] * order[PRICE] > self._participants[participant_id][CASH]:
                raise ValueError("insufficient funds")
            self._buy_order_queue.put((-price, order))
        elif action == SELL:
            if order[AMOUNT] > self._participants[participant_id][SECURITY]:
                raise ValueError("insufficient security holdings")
            self._sell_order_queue.put((price, order))
        else:
            raise ValueError("action must be BUY or SELL")
        self.tape.append((ORDER, order))

    def try_match_trade(self) -> bool:
        try:
            generous_buy_queue_elt = self._buy_order_queue.get()
            generous_sell_queue_elt = self._sell_order_queue.get()
            generous_buy = generous_buy_queue_elt[1]
            generous_sell = generous_sell_queue_elt[1]
        except Empty:
            return False
        if generous_buy[PRICE] < generous_sell[PRICE]:
            return False

        if generous_buy[AMOUNT] >= generous_sell[AMOUNT]:
            generous_buy_queue_elt[1][AMOUNT] = (
                generous_buy[AMOUNT] - generous_sell[AMOUNT]
            )
            self._buy_order_queue.put(generous_buy_queue_elt)
        else:
            generous_sell_queue_elt[1][AMOUNT] = (
                generous_sell[AMOUNT] - generous_buy[AMOUNT]
            )
            self._sell_order_queue.put(generous_sell_queue_elt)
        self.tape.append((MATCH, generous_buy, generous_sell))
        return True


class Participant:
    
