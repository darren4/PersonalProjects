from typing import List

from trading.backtrading.strategy_interface import (
    StrategyInterface,
    Holdings,
    Trade,
    TradeAction,
    TradingWindow,
)


class StrategyLinearRegression(StrategyInterface):
    def __init__(self):
        self._price_count: int = 0
        self._var_price_count: float = 0
        self._covariance: float = 0
        self._avg_price_count: float = 0
        self._avg_price: float = 0

        self._price: float = 0
        self._holding: int = 0

    def _add_price(self, price: float) -> None:
        # TODO: make x and n different
        self._price_count += 1
        delta_price_count: float = self._price_count - self._avg_price_count
        delta_price: float = price - self._avg_price
        try:
            self._var_price_count += (((self._price_count-1)/self._price_count)*delta_price_count*delta_price_count - self._var_price_count)/self._price_count
            self._covariance += (((self._price_count-1)/self._price_count)*delta_price_count*delta_price - self._covariance)/self._price_count
            self._avg_price_count += delta_price_count / self._avg_price_count
            self._avg_price += delta_price / self._avg_price_count
        except ZeroDivisionError:
            pass

    def _trending_up(self) -> bool:
        try:
            return self._covariance / self._var_price_count > 0
        except ZeroDivisionError:
            return False

    def add_historical_data(self, windows: List[TradingWindow]) -> None:
        self._price = windows[0].prices.close
        for window in windows:
            self._add_price(window.prices.close)

    def set_holdings(self, holdings: Holdings) -> None:
        self._cash = holdings.cash

    def trade(self) -> List[Trade]:
        if self._trending_up():
            if not self._holding:
                self._holding = int(self._cash / self._price)
                return [Trade(TradeAction.OPEN_LONG, self._holding)]
        elif self._holding:
            current: int = self._holding
            self._holding = 0
            return [Trade(TradeAction.CLOSE_LONG, current)]
        return list()
