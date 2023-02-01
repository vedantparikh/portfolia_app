import pandas as pd
from ta.volatility import (
    AverageTrueRange,
    BollingerBands,
)

from portfolio.python.streamlit.statistical_indicators.base import BaseIndicator


class VolatilityIndicators(BaseIndicator):
    """ Returns a Pandas Dataframe with calculated different Volatility Indicators. """

    def bollinger_bands_indicator(self, window: int = 20, window_dev: int = 2, fillna: bool = False):
        """
        Bollinger Bands are a technical analysis tool used in finance to measure the volatility of an asset.
        They consist of three lines drawn on a chart: a simple moving average in the middle, with an upper and
        lower band plotted two standard deviations away from the average. The bands will expand during periods of
        high volatility and contract during periods of low volatility, providing traders with a visual representation
        of an asset's price volatility. The theory is that prices tend to stay within the upper and lower bands,
        and that changes in volatility can be used to make trading decisions.
        https://school.stockcharts.com/doku.php?id=technical_indicators:bollinger_bands
        :param window: N -period.
        :param window_dev: N -factor standard deviation
        :param fillna: If True, fil NaN values.
        :return: DataFrame with bollinger bands indicator fields.
        """
        bollinger_bands = BollingerBands(close=self.df.Close, window=window, window_dev=window_dev, fillna=fillna)
        self.df['bb_bbm'] = bollinger_bands.bollinger_mavg()
        self.df['bb_bbh'] = bollinger_bands.bollinger_hband()
        self.df['bb_bbl'] = bollinger_bands.bollinger_lband()
        # Add Bollinger Band high indicator
        self.df['bb_bbhi'] = bollinger_bands.bollinger_hband_indicator()
        # Add Bollinger Band low indicator
        self.df['bb_bbli'] = bollinger_bands.bollinger_lband_indicator()

        return self.df

    def average_true_range_indicator(self, window: int = 14, fillna: bool = False) -> pd.DataFrame:
        """
        The ATR is calculated by taking the average of the true ranges over a specified number of days.
        A true range is defined as the greatest of the following:
            The current high minus the current low
            The absolute value of the current high minus the previous close
            The absolute value of the current low minus the previous close

        The ATR is expressed as a single value, representing the average range of price movement over the specified
        number of days. A higher ATR indicates a higher degree of price volatility, while a lower ATR suggests lower
        price volatility.
        In summary, the ATR is used to measure the average daily price range for a financial instrument, and provides
        insight into the instrument's volatility.
        :param window: N -Period.
        :param fillna: If True, fill NaN values.
        :return: DataFrame with Average True Range indicator fields.
        """

        average_true_range = AverageTrueRange(
            high=self.df.High, low=self.df.Low, close=self.df.Close, window=window, fillna=fillna
        )
        self.df['average_true_range'] = average_true_range.average_true_range()

        return self.df

    def all_volatility_indicators(self) -> pd.DataFrame:
        """
        Applies all volatility indicators.
        :return: DataFrame with the all defined volatility indicators.
        """
        self.df = self.bollinger_bands_indicator()
        self.df = self.average_true_range_indicator()

        return self.df
