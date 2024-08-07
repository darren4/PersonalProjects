from abc import ABC, abstractmethod
from typing import List, NoReturn
from dataclasses import dataclass
from datetime import date
from enum import StrEnum


@dataclass
class TradingDay:
    day: date
    close: float
    volume: int

class TradeAction(StrEnum):
    BUY = "BUY"
    SELL = "SELL"
    CLOSE = "CLOSE"

@dataclass
class Trade:
    action: TradeAction
    amount: int


class StrategyInterface(ABC):
    @abstractmethod
    def get_historical_data(self, days: List[TradingDay]) -> NoReturn:
        pass

    @abstractmethod
    def trade(self) -> List[TradeAction]:
        pass
