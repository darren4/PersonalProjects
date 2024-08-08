from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass
from datetime import date
from enum import StrEnum


@dataclass
class TradingDay:
    day: date
    price: float
    volume: int

class TradeAction(StrEnum):
    BUY = "BUY"
    SELL = "SELL"

@dataclass
class Trade:
    action: TradeAction
    amount: int

@dataclass
class Holdings:
    cash: float
    equity: int

class StrategyInterface(ABC):
    @abstractmethod
    def add_historical_data(self, days: List[TradingDay]) -> None:
        pass

    @abstractmethod
    def set_holdings(self, holdings: Holdings) -> None:
        pass

    @abstractmethod
    def trade(self) -> List[Trade]:
        pass
