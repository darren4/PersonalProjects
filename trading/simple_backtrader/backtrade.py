from trading.simple_backtrader import SimpleBacktrader
from trading.simple_backtrader.strategy_random import random_short, random_long
from trading.simple_backtrader.strategy_ma import simple_ma
from trading.simple_backtrader.strategy_trend_follow import linear_trend_follow

import time
import pandas as pd
import os


historical_data = pd.read_csv(
    f"{os.environ['PYTHONPATH']}/trading/historical_data/Yahoo-Data/AAPL.csv"
).to_dict("records")
STARING_CASH = 10000

simple_backtrader = SimpleBacktrader(historical_data, STARING_CASH)
start_time = time.time()
final_portfolio_value = simple_backtrader.backtrade(linear_trend_follow)
end_time = round(time.time() - start_time, 2)
print(f"Backtrading took {end_time} seconds")

print(f"[SUMMARY] Starting value: {STARING_CASH}")
print(f"[SUMMARY] Ending value:   {round(final_portfolio_value, 2)}")
