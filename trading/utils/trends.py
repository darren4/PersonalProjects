import numpy as np
from sklearn.svm import SVR


class TrendDirection:
    def projection(self, history: list, projection_len: int) -> float:
        raise NotImplementedError()

    def following_trend(self, holding_for: int, current_price: float) -> bool:
        raise NotImplementedError()


class LinearTrendDirection(TrendDirection):
    def __init__(self, _error_proportion=0.2):
        self.error_proportion = _error_proportion
        self.slope = np.NAN
        self.intercept = np.NAN
        self.history_len = np.NAN

    def projection(self, history: list, projection_len: int) -> float:
        self.history_len = len(history)
        x_axis = np.array(range(self.history_len))
        x_axis = np.vstack([x_axis, np.ones(len(x_axis))]).T
        self.slope, self.intercept = np.linalg.lstsq(
            x_axis, np.array(history), rcond=None
        )[0]
        return (self.slope * (projection_len + self.history_len)) + self.intercept

    def following_trend(self, holding_for: int, current_price: float) -> bool:
        total_projected_delta = self.slope * (self.history_len + holding_for)
        projected_price = total_projected_delta + self.intercept
        return abs(projected_price - current_price) < (
            self.error_proportion * total_projected_delta
        )


class LogisticTrendDirection(TrendDirection):
    def __init__(self, _error_proportion=0.2):
        self.error_proportion = _error_proportion
        self.logistic_regressor = SVR()
        self.zero_prediction = np.NAN
        self.history_len = np.NAN

    def projection(self, history: list, projection_len: int) -> float:
        self.history_len = len(history)
        x_axis = np.array(range(self.history_len)).reshape(-1, 1)
        self.logistic_regressor.fit(x_axis, np.array(history))
        self.zero_prediction = self.logistic_regressor.predict(
            np.array([0]).reshape(-1, 1)
        )[0]
        return self.logistic_regressor.predict(
            np.array([self.history_len + projection_len]).reshape(-1, 1)
        )[0]

    def following_trend(self, holding_for: int, current_price: float) -> bool:
        projected_price = self.logistic_regressor.predict(
            np.array([self.history_len + holding_for]).reshape(-1, 1)
        )[0]
        total_projected_delta = projected_price - self.zero_prediction
        return abs(projected_price - current_price) < (
            self.error_proportion * total_projected_delta
        )
