import pandas as pd
from ta.trend import (
    ADXIndicator,
    AroonIndicator,
    MACD,
    PSARIndicator,
)

from portfolio.python.streamlit.statistical_indicators.base import BaseIndicator


class TrendIndicators(BaseIndicator):
    """ Returns a Pandas Dataframe with calculated different Trend Indicators. """

    def macd_indicator(
            self, window_slow: int = 26, window_fast: int = 12, window_sign: int = 9, fillna: bool = False
    ) -> pd.DataFrame:
        """
        Moving Average Convergence Divergence (MACD)
        Is a trend-following momentum indicator that shows the relationship between two moving averages of prices.
        https://school.stockcharts.com/doku.php?id=technical_indicators:moving_average_convergence_divergence_macd
        :param window_slow: N -Period long term.
        :param window_fast: N -Period short term.
        :param window_sign: N -Period to signal.
        :param fillna: if True, fill NaN values.
        :return: DataFrame with the MACD indicator fields.
        """
        macd = MACD(close=self.df.Close, window_slow=window_slow, window_fast=window_fast, window_sign=window_sign,
                    fillna=fillna)
        self.df['MACD'] = macd.macd()
        self.df['Signal'] = macd.macd_signal()
        self.df['Histogram'] = macd.macd_diff()

        return self.df

    def adx_indicator(self, window: int = 14, fillna: bool = False) -> pd.DataFrame:
        """
        Average Directional Movement Index (ADX)
        The Plus Directional Indicator (+DI) and Minus Directional Indicator (-DI) are derived from smoothed averages of
         these differences, and measure trend direction over time. These two indicators are often referred to
         collectively as the Directional Movement Indicator (DMI).
        The Average Directional Index (ADX) is in turn derived from the smoothed averages of the difference between +DI
        and -DI, and measures the strength of the trend (regardless of direction) over time.
        Using these three indicators together, chartists can determine both the direction and strength of the trend.
        http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:average_directional_index_adx
        :param window: N -Period.
        :param fillna: if True, fill NaN values.
        :return: DataFrame with ADX indicator fields.
        """
        adx = ADXIndicator(high=self.df.High, low=self.df.Low, close=self.df.Close, window=window, fillna=fillna)
        self.df['adx'] = adx.adx()
        self.df['adx_neg'] = adx.adx_neg()
        self.df['adx_pos'] = adx.adx_pos()

        return self.df

    def aroon_indicator(self, window: int = 25, fillna: bool = False) -> pd.DataFrame:
        """
        Aroon Indicator
        Identify when trends are likely to change direction.
        Aroon Up = ((N - Days Since N-day High) / N) x 100 Aroon Down = ((N - Days Since N-day Low) / N) x 100
        Aroon Indicator = Aroon Up - Aroon Down
        https://www.investopedia.com/terms/a/aroon.asp
        :param window: N -Period.
        :param fillna: if True, fill NaN values.
        :return: DataFrame with Aroon indicator fields.
        """
        aroon = AroonIndicator(close=self.df.Close, window=window, fillna=fillna)
        self.df['aroon_down'] = aroon.aroon_down()
        self.df['aroon_up'] = aroon.aroon_up()
        self.df['aroon_indicator'] = aroon.aroon_indicator()

        return self.df

    def psar_indicator(self, step: float = 0.02, max_step: float = 0.2, fillna: bool = False) -> pd.DataFrame:
        """
        Parabolic Stop and Reverse (Parabolic SAR)
        The Parabolic Stop and Reverse, more commonly known as the Parabolic SAR,is a trend-following indicator
        developed by J. Welles Wilder. The Parabolic SAR is displayed as a single parabolic line (or dots) underneath
        the price bars in an uptrend, and above the price bars in a downtrend.
        https://school.stockcharts.com/doku.php?id=technical_indicators:parabolic_sar
        :param step: Acceleration Factor used to compute the SAR.
        :param max_step: Maximum value allowed for the Acceleration Factor.
        :param fillna:  If True, fill nan values.
        :return: DataFrame with the PSAR indicator fields.
        """
        psar = PSARIndicator(
            high=self.df.High, low=self.df.Low, close=self.df.Close, step=step, max_step=max_step, fillna=fillna
        )
        self.df['psar'] = psar.psar()
        self.df['psar_down'] = psar.psar_down()
        self.df['psar_down_indicator'] = psar.psar_down_indicator()
        self.df['psar_up'] = psar.psar_up()
        self.df['psar_up_indicator'] = psar.psar_up_indicator()

        return self.df

    def all_trend_indicators(self) -> pd.DataFrame:
        """
        Applies all trend indicators.
        :return: DataFrame with the all defined trend indicators.
        """
        self.df = self.macd_indicator()
        self.df = self.aroon_indicator()
        self.df = self.adx_indicator()
        self.df = self.psar_indicator()

        return self.df
