from trading.simple_backtrader.constants import *
from trading.utils.trends import LinearTrendDirection

import pandas as pd


trender = LinearTrendDirection()


def linear_trend_follow(historical_data: list, position: dict):
    historical_data = pd.DataFrame(historical_data)
    current_price = historical_data["Close"].iloc[-1]
    trades = []
    if len(historical_data) > 11:
        recent_history = list(historical_data["Close"].iloc[-11:-1])
        projection = trender.projection(recent_history, 5)
        if projection > current_price:
            trades.append((CLOSE_SELL, position[SHORT]))
            if position[LONG] == 0:
                trades.append((BUY, 1))
        else:
            trades.append((CLOSE_BUY, position[LONG]))
            if position[SHORT] == 0:
                trades.append((SELL, 1))
    return trades
