from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


@dataclass
class Prices:
    open: float
    high: float
    low: float
    close: float


@dataclass(order=True)
class TradingWindow:
    time: datetime
    prices: Prices
    volume: int


class TradeAction(StrEnum):
    OPEN_LONG = "OPEN_LONG"
    CLOSE_LONG = "CLOSE_LONG"
    OPEN_SHORT = "OPEN_SHORT"
    CLOSE_SHORT = "CLOSE_SHORT"


@dataclass
class Trade:
    action: TradeAction
    amount: int


@dataclass
class Holdings:
    cash: float
    long_shares: int
    short_shares: int


class StrategyInterface(ABC):
    @abstractmethod
    def add_historical_data(self, windows: List[TradingWindow]) -> None:
        pass

    @abstractmethod
    def set_holdings(self, holdings: Holdings) -> None:
        pass

    @abstractmethod
    def trade(self) -> List[Trade]:
        pass
