from trading.simple_backtrader.constants import *

from collections import deque
from typing import Callable


class SimpleBacktrader:
    def __init__(
        self, _historical_data: list, _starting_cash: float, _data_col: str = "Close"
    ):
        self.historical_data = _historical_data
        self.data_col = _data_col
        self.reset_position = {CASH: _starting_cash, LONG: 0, SHORT: 0}
        self.position = None
        self.short_queue = None
        self.user_historical_data = None

        self.processing = {
            BUY: self._process_buy,
            SELL: self._process_sell,
            CLOSE_BUY: self._process_close_buy,
            CLOSE_SELL: self._process_close_sell,
        }

    def _process_buy(self, amount, current_price):
        action_value = current_price * amount
        if self.position[CASH] < action_value:
            print(
                f"[WARNING] Cash amount {self.position[CASH]} less than purchase value {action_value}"
            )
        else:
            self.position[CASH] -= action_value
            self.position[LONG] += amount

    def _process_sell(self, amount, current_price):
        self.position[SHORT] += amount
        self.short_queue.appendleft({AMOUNT: amount, OPEN_PRICE: current_price})

    def _process_close_buy(self, amount, current_price):
        if self.position[LONG] < amount:
            print(
                f"[WARNING] Close amount {amount} less than held {self.position[LONG]}"
            )
        else:
            self.position[LONG] -= amount
            self.position[CASH] += amount * current_price

    def _process_close_sell(self, amount, current_price):
        while amount > 0:
            if len(self.short_queue) == 0:
                print(f"[WARNING] Short queue empty before short amount closed")
                return
            trade_amount = self.short_queue[-1][AMOUNT]
            if self.position[CASH] < trade_amount * self.short_queue[-1][OPEN_PRICE]:
                print(
                    f"[WARNING] Insufficient cash {self.position[CASH]} to close short position"
                )
                return

            if amount > trade_amount:
                amount -= trade_amount
                self.position[CASH] += trade_amount * (
                    self.short_queue[-1][OPEN_PRICE] - current_price
                )
                self.short_queue.pop()
            else:
                self.position[CASH] += amount * (
                    self.short_queue[-1][OPEN_PRICE] - current_price
                )
                self.short_queue[-1][AMOUNT] = trade_amount - amount
                break
        self.position[SHORT] -= amount

    def _process_trades(self, trades):
        if trades:
            for action, amount in trades:
                if amount > 0:
                    current_price = self.user_historical_data[-1][self.data_col]
                    try:
                        self.processing[action](amount, current_price)
                    except KeyError:
                        print(
                            f"[WARNING] Unidentified action: {action} - no trade performed"
                        )
                    assert not self.position[CASH] < 0

    def backtrade(self, strategy: Callable[[list, dict], list]) -> float:
        self.user_historical_data = list()
        self.position = self.reset_position
        self.short_queue = deque()
        for point in self.historical_data:
            self.user_historical_data.append(point)

            if (self.position[CASH] + (self.position[LONG] * point[self.data_col])) < (
                self.position[SHORT] * point[self.data_col] * 1.5
            ):
                print(
                    f"[ERROR] Security price went to {point['Close']} leading to margin call with position {self.position}"
                )
                break

            trades = strategy(self.user_historical_data, self.position)
            self._process_trades(trades)

        final_price = self.user_historical_data[-1][self.data_col]
        final_short_value = 0
        while len(self.short_queue) > 0:
            short_trade = self.short_queue.pop()
            final_short_value += (short_trade[OPEN_PRICE] - final_price) * short_trade[
                AMOUNT
            ]
        final_portfolio_value = (
            self.position[CASH]
            + (self.position[LONG] * final_price)
            + final_short_value
        )
        return final_portfolio_value
