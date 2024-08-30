import requests
from requests import Response
import os
from typing import List, Dict
from datetime import datetime

from trading.backtrading.strategy_interface import TradingWindow, Prices
from trading.backtrading.trading_simulator import TradingSimulator


def get_weekly_data(symbol: str) -> List[TradingWindow]:
    alphavantage_key: str = os.getenv("ALPHA_VANTAGE_KEY")
    if not alphavantage_key:
        raise RuntimeError("ALPHA_VANTAGE_KEY missing")

    url: str = "https://www.alphavantage.co/query"
    params: Dict[str, str] = {
        "function": "TIME_SERIES_WEEKLY_ADJUSTED",
        "symbol": symbol,
        "apikey": alphavantage_key,
    }
    response: Response = requests.get(url=url, params=params)
    response.raise_for_status()

    return sorted(
        [
            TradingWindow(
                datetime.strptime(date_str, "%Y-%m-%d"),
                Prices(
                    float(prices_dict["1. open"]),
                    float(prices_dict["2. high"]),
                    float(prices_dict["3. low"]),
                    float(prices_dict["5. adjusted close"]),
                ),
                int(prices_dict["6. volume"]),
            )
            for date_str, prices_dict in response.json()[
                "Weekly Adjusted Time Series"
            ].items()
        ]
    )


if __name__ == "__main__":
    windows: List[TradingWindow] = get_weekly_data("MSFT")

    from trading.backtrading.strategy_buyhold import StrategyBuyHold 
    from trading.backtrading.strategy_linear_regression import StrategyLinearRegression

    print(TradingSimulator(windows, 1000000.0).backtrade_strategy(StrategyBuyHold()))
    print(TradingSimulator(windows, 1000000.0).backtrade_strategy(StrategyLinearRegression()))
