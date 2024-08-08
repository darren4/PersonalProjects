from trading.backtrading.strategy_interface import TradingDay, TradeAction, Trade, Holdings, StrategyInterface

from typing import List, Final
from dataclasses import dataclass
from queue import Queue


MARGIN_CALL_RATIO: Final[float] = 1.5


@dataclass
class Short:
    amount: int
    price: float


class Backtrader:
    def __init__(self, historical_data: List[TradingDay], starting_cash: float) -> None:
        self._historical_data: List[TradingDay] = historical_data
        self._starting_cash: float = starting_cash

    def backtrade_strategy(self, strategy: StrategyInterface) -> float:
        holdings: Holdings = Holdings(self._starting_cash, 0)
        strategy.set_holdings(holdings)
        open_shorts: Queue = Queue()
        for trading_day in self._historical_data:
            if holdings.cash < (trading_day.price * -holdings.equity * MARGIN_CALL_RATIO):
                print("Margin called")
                return 0.0

            strategy.add_historical_data([trading_day])
            trades: List[TradeAction] = strategy.trade()
            for trade in trades:
                if trade.action == TradeAction.BUY:
                    transaction_value: float = trade.amount * trading_day.price
                    if holdings.cash < transaction_value:
                        raise ValueError(f"{holdings.cash} insufficient to buy {trade.amount} at {trading_day.price}")
                    holdings.cash -= transaction_value
                    holdings.equity += trade.amount
                elif trade.action == TradeAction.SELL:
                    
                else:
                    raise NotImplementedError()
