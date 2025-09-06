import numpy as np
import pandas as pd
from ta.trend import EMAIndicator


class MACDStrategy:
    """
    Inspired from the video: https://www.youtube.com/watch?v=rf_EQvubKlk&list=LL&index=1
    Take away points:
        1. We have MACD line (12 days average), Signal line (26 days average), histogram. Histogram indicates
        difference between MACD line and Signal line, smaller the difference, smaller histogram and vice versa.
        2. If MACD line crosses above Signal line and both happens below zero then it's a Buy signal from pure MACD
        indicator.
        3. If MACD line crosses below Signal line and both happens above zero then it's a Sell signal from pure MACD
        indicator.
        4. Strength of Buy and Sell can be interpreted from the histogram, if high histogram the stronger Buy/Sell
        indications.  If histogram is below zero line that indicates sell and vice versa.
        5. Only MACD is not good enough to reduce out False Positive and False Negative Buy/Sell indications.
        Adding 200 days exponential moving average, can leverage the strength of indication. If price is above the 200
        days mavg then the trend is upwards and downwards otherwise. So when the trend is upwards and also MACD line
        crosses above Signal line at below zero line that's our cue to Buy and if the trend is downwards and also
        MACD line crosses below Signal line at above zero line that's our cue to Sell.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        # we should receive DataFrame with the MACD fields, No need to calculate again.
        self.df = df

        assert {"MACD", "Signal", "Histogram"}.issubset(df.columns), (
            "MACD trend calculated fields are not present in DataFrame."
        )

    def _find_intersection(self, x: float, y: float, digits: int = 0) -> int:
        """
        Calculates tentative intersection point for the lines.
        :param x: Point on first line/series.
        :param y: Point on second line/series.
        :param digits: Round number for calculating intersection.
        """
        try:
            if round(x, digits) == round(y, digits):
                return 1
            else:
                return 0
        except ValueError:
            return 0

    def _get_closing_price_difference(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates closing price difference between buy and sell indicators, to get better idea about the price
        movement.
        :param df: DaaFrame with the buy/sell indicators.
        :returns: Returns the DataFrame with the closing price difference.
        """
        ith_row = None
        for i in df.index:
            if df.loc[i, "MACD_intersection"].any():
                if not ith_row:
                    ith_row = i
                    df.loc[i, "MACD_price_difference"] = np.nan
                else:
                    df.loc[i, "MACD_price_difference"] = (
                        df.loc[i, "Close"] - df.loc[ith_row, "Close"]
                    )
                    ith_row = i
            else:
                df.loc[i, "MACD_price_difference"] = np.nan

        return df

    def _get_buy_sell_calls(
        self, df: pd.DataFrame, condition_days: int = 10
    ) -> pd.DataFrame:
        """
        Calculates Buy/Sell signals.
        :param df: DataFrame with the MACD intersection column.
        :param condition_days: Number of days the condition for the buy or sell should be satisfied.
        :return: Returns the DataFrame with the Buy and Sell calls.
        """
        # We will use 1 as Buy call and -1 as Sell call. From intersection logic we received 1 wherever intersection
        # happened and in this method we will replace them appropriately by 1 or -1 depending on strategy and
        # conditions.
        for i in range(df.shape[0]):
            # 26 as initial 26 value of Signal will be `Null` because of the 26-day moving average calculation.
            if i > 26:
                if df["MACD_intersection"][i] == 1:
                    # getting last number of condition days values (days) of MACD and Signal for comparison.
                    macd = df["MACD"][i - condition_days : i].tolist()
                    signal = df["Signal"][i - condition_days : i].tolist()
                    states = []
                    for m, s in zip(macd, signal):
                        # for last condition_days values if MACD value is less than the Signal value and also both
                        # values are less than the zero value we append `True` to track how many times it happened for
                        # past condition_days days.
                        if m < s and m < 0 and s < 0:
                            states.append(True)
                        # for last condition_days values if MACD value is greater than the Signal value and also both
                        # values are greater than the zero value we append `True` to track how many times it happened
                        # for past condition_days.
                        elif m > s and m > 0 and s > 0:
                            states.append(False)
                        # if above condition is not matched we skip appending `True` or `False` value as we need to be
                        # sure that all the values were not tangled with each other and not generating weak buy/sell
                        # signals.
                    # all past days should have either `True` or `False` values.
                    c = all(state is True for state in states) or all(
                        state is False for state in states
                    )
                    # We are not interested if we did not receive condition_days states.
                    if len(states) == condition_days:
                        if (
                            c
                            and (df["MACD"][i] <= df["Signal"][i] < 0)
                            and df["Close"][i] >= df["MACD_EMA"][i]
                        ):
                            # Keeping the value 1 as it's a Buy call.
                            continue
                        elif (
                            c
                            and (df["MACD"][i] >= df["Signal"][i] > 0)
                            and df["Close"][i] <= df["MACD_EMA"][i]
                        ):
                            # Changing the value to -1 as it's a Sell call.
                            df["MACD_intersection"].iloc[i] = -1
                    else:
                        # If states are less than condition_days we should change the intersection value 1 to 0 else it
                        # will be considered as a Buy signal.
                        df["MACD_intersection"].iloc[i] = 0

        df = self._get_closing_price_difference(df=df)
        df["MACD_intersection"] = abs(df["MACD_intersection"]) * df["MACD"]
        df["MACD_intersection"] = df["MACD_intersection"].replace(0, np.nan)

        return df

    def buy_sell_strategy(
        self, condition_days: int = 10, moving_average_days: int = 200
    ):
        """
        :return: DataFrame with the MACD Buy and Sell signals.
        """
        # initial intersection mappings
        self.df["MACD_intersection"] = self.df.apply(
            lambda row: self._find_intersection(row["MACD"], row["Signal"]), axis=1
        )
        self.df["MACD_EMA"] = EMAIndicator(
            close=self.df.Close, window=moving_average_days
        ).ema_indicator()
        self.df = self._get_buy_sell_calls(df=self.df, condition_days=condition_days)
        self.df.rename(columns={"MACD_intersection": "MACD_buy_or_sell"}, inplace=True)

        return self.df
