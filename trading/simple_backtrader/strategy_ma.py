from trading.simple_backtrader.constants import *

import pandas as pd
import numpy as np


def simple_ma(historical_data: list, position: dict):
    historical_data = pd.DataFrame(historical_data)
    trades = []
    if len(historical_data) > 6:
        ma = np.average(np.array(historical_data["Close"].iloc[-5:-1]))
        if historical_data["Close"].iloc[-1] > ma:
            trades.append((CLOSE_SELL, position[SHORT]))
            if position[LONG] == 0:
                trades.append((BUY, 1))
        elif historical_data["Close"].iloc[-1] < ma:
            trades.append((CLOSE_BUY, position[LONG]))
            if position[SHORT] == 0:
                trades.append((SELL, 1))
    return trades
