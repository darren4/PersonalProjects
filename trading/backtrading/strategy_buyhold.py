from typing import List

from trading.backtrading.strategy_interface import (
    StrategyInterface,
    Holdings,
    Trade,
    TradeAction,
    TradingWindow,
)


class StrategyBuyHold(StrategyInterface):
    def __init__(self):
        self._bought: bool = False
        self._price: float = 0.0
        self._cash: float = 0

    def add_historical_data(self, windows: List[TradingWindow]) -> None:
        self._price = windows[0].prices.close

    def set_holdings(self, holdings: Holdings) -> None:
        self._cash = holdings.cash

    def trade(self) -> List[Trade]:
        if not self._bought:
            self._bought = True
            return [Trade(TradeAction.OPEN_LONG, int(self._cash / self._price))]
        else:
            return list()
