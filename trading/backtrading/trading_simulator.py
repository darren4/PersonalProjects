from trading.backtrading.strategy_interface import (
    TradingWindow,
    TradeAction,
    Trade,
    Holdings,
    StrategyInterface,
)

from typing import List, Final, Deque
from dataclasses import dataclass
from collections import deque


MARGIN_CALL_RATIO: Final[float] = 1.5


@dataclass
class Short:
    amount: int
    price: float


class TradingSimulator:
    def __init__(
        self, historical_data: List[TradingWindow], starting_cash: float
    ) -> None:
        self._historical_data: List[TradingWindow] = historical_data
        self._starting_cash: float = starting_cash

    def backtrade_strategy(self, strategy: StrategyInterface) -> float:
        holdings: Holdings = Holdings(self._starting_cash, 0, 0)
        strategy.set_holdings(holdings)
        open_shorts: Deque[Short] = deque()
        for trading_window in self._historical_data:
            account_assets_value: float = holdings.cash + (
                holdings.long_shares * trading_window.prices.open
            )
            account_liability_value: float = (
                trading_window.prices.open * holdings.short_shares
            )
            if account_assets_value < account_liability_value * MARGIN_CALL_RATIO:
                print("Margin called")
                return 0.0

            strategy.add_historical_data([trading_window])
            trades: List[Trade] = strategy.trade()
            transaction_share_price: float = trading_window.prices.close
            for trade in trades:
                if trade.action == TradeAction.OPEN_LONG:
                    transaction_value: float = trade.amount * transaction_share_price
                    if holdings.cash < transaction_value:
                        raise ValueError(
                            f"{holdings.cash} insufficient to buy {trade.amount} at closing price {transaction_share_price}"
                        )
                    holdings.cash -= transaction_value
                    holdings.long_shares += trade.amount
                elif trade.action == TradeAction.CLOSE_LONG:
                    transaction_share_count: int = min(
                        trade.amount, holdings.long_shares
                    )
                    transaction_value: float = (
                        transaction_share_count * transaction_share_price
                    )
                    holdings.cash += transaction_value
                    holdings.long_shares -= transaction_share_count
                elif trade.action == TradeAction.OPEN_SHORT:
                    holdings.short_shares += trade.amount
                    open_shorts.appendleft(Short(trade.amount, transaction_share_price))
                elif trade.action == TradeAction.CLOSE_SHORT:
                    remaning_share_count: int = trade.amount
                    exchange_difference: float = (
                        open_shorts[-1].price - transaction_share_price
                    )
                    while open_shorts and remaning_share_count:
                        if open_shorts[-1].amount <= remaning_share_count:
                            short: Short = open_shorts.pop()
                            holdings.cash += short.amount * exchange_difference
                            remaning_share_count -= short.amount
                            holdings.short_shares -= short.amount
                        else:
                            holdings.cash += remaning_share_count * exchange_difference
                            open_shorts[-1].amount -= remaning_share_count
                            holdings.short_shares -= remaning_share_count
                            remaning_share_count = 0
                else:
                    raise NotImplementedError(trade.action)

            strategy.set_holdings(holdings)

        last_close: float = self._historical_data[-1].prices.close
        for short in open_shorts:
            holdings.cash += short.amount * (short.price - last_close)

        holdings.cash += holdings.long_shares * last_close
        return holdings.cash
