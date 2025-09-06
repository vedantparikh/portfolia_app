import numpy as np
import polars as pl


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

    def __init__(self, df: pl.DataFrame) -> None:
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

    def _get_closing_price_difference(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Calculates closing price difference between buy and sell indicators, to get better idea about the price
        movement.
        :param df: DataFrame with the buy/sell indicators.
        :returns: Returns the DataFrame with the closing price difference.
        """
        # Convert to pandas for easier manipulation, then back to polars
        pd_df = df.to_pandas()
        ith_row = None

        for i in pd_df.index:
            if pd_df.loc[i, "MACD_intersection"] == 1:
                if not ith_row:
                    ith_row = i
                    pd_df.loc[i, "MACD_price_difference"] = np.nan
                else:
                    pd_df.loc[i, "MACD_price_difference"] = (
                        pd_df.loc[i, "Close"] - pd_df.loc[ith_row, "Close"]
                    )
                    ith_row = i
            else:
                pd_df.loc[i, "MACD_price_difference"] = np.nan

        return pl.from_pandas(pd_df)

    def _get_buy_sell_calls(
        self, df: pl.DataFrame, condition_days: int = 10
    ) -> pl.DataFrame:
        """
        Calculates Buy/Sell signals.
        :param df: DataFrame with the MACD intersection column.
        :param condition_days: Number of days the condition for the buy or sell should be satisfied.
        :return: Returns the DataFrame with the Buy and Sell calls.
        """
        # Convert to pandas for easier manipulation, then back to polars
        pd_df = df.to_pandas()

        # We will use 1 as Buy call and -1 as Sell call. From intersection logic we received 1 wherever intersection
        # happened and in this method we will replace them appropriately by 1 or -1 depending on strategy and
        # conditions.
        for i in range(pd_df.shape[0]):
            # 26 as initial 26 value of Signal will be `Null` because of the 26-day moving average calculation.
            if i > 26:
                if pd_df["MACD_intersection"][i] == 1:
                    # getting last number of condition days values (days) of MACD and Signal for comparison.
                    macd = pd_df["MACD"][i - condition_days : i].tolist()
                    signal = pd_df["Signal"][i - condition_days : i].tolist()
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
                        # sure about the trend.
                        # all past days should have either `True` or `False` values.
                    c = all(state is True for state in states) or all(
                        state is False for state in states
                    )
                    # We are not interested if we did not receive condition_days states.
                    if len(states) == condition_days:
                        if (
                            c
                            and (pd_df["MACD"][i] <= pd_df["Signal"][i] < 0)
                            and pd_df["Close"][i] >= pd_df["MACD_EMA"][i]
                        ):
                            # Keeping the value 1 as it's a Buy call.
                            continue
                        elif (
                            c
                            and (pd_df["MACD"][i] >= pd_df["Signal"][i] > 0)
                            and pd_df["Close"][i] <= pd_df["MACD_EMA"][i]
                        ):
                            # Changing the value to -1 as it's a Sell call.
                            pd_df["MACD_intersection"].iloc[i] = -1
                    else:
                        # If states are less than condition_days we should change the intersection value 1 to 0 else it
                        # will be considered as a Buy signal.
                        pd_df["MACD_intersection"].iloc[i] = 0

        # Convert back to polars
        result_df = pl.from_pandas(pd_df)
        result_df = self._get_closing_price_difference(df=result_df)

        # Apply final transformations
        result_df = result_df.with_columns(
            [
                (pl.col("MACD_intersection").abs() * pl.col("MACD")).alias(
                    "MACD_intersection"
                )
            ]
        )

        # Replace 0 with NaN
        result_df = result_df.with_columns(
            [
                pl.when(pl.col("MACD_intersection") == 0)
                .then(None)
                .otherwise(pl.col("MACD_intersection"))
                .alias("MACD_intersection")
            ]
        )

        return result_df

    def buy_sell_strategy(
        self, condition_days: int = 10, moving_average_days: int = 200
    ):
        """
        :return: DataFrame with the MACD Buy and Sell signals.
        """
        # Calculate EMA using polars
        self.df = self.df.with_columns(
            [pl.col("Close").ewm_mean(span=moving_average_days).alias("MACD_EMA")]
        )

        # Calculate intersections
        self.df = self.df.with_columns(
            [
                pl.map_rows(
                    [pl.col("MACD"), pl.col("Signal")],
                    lambda row: self._find_intersection(row[0], row[1]),
                ).alias("MACD_intersection")
            ]
        )

        # Get buy/sell calls
        self.df = self._get_buy_sell_calls(df=self.df, condition_days=condition_days)

        # Rename column
        self.df = self.df.rename({"MACD_intersection": "MACD_buy_or_sell"})

        return self.df
