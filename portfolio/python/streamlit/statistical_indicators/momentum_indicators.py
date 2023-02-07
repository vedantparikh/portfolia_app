import pandas as pd
from statistical_indicators.base import BaseIndicator
from ta.momentum import (ROCIndicator, RSIIndicator, StochRSIIndicator, StochasticOscillator)


class MomentumIndicators(BaseIndicator):
    """ Returns a Pandas Dataframe with calculated different Momentum Indicators. """

    def rsi_indicator(self, window: int = 14, fillna: bool = False) -> pd.DataFrame:
        """
        Relative Strength Index (RSI)
        Compares the magnitude of recent gains and losses over a specified time period to measure speed and change
        of price movements of a security. It is primarily used to attempt to identify overbought or oversold conditions
        in the trading of an asset.
        https://www.investopedia.com/terms/r/rsi.asp
        :param window: N -Period.
        :param fillna: If True, fill NaN values.
        :return: DataFrame with RSI indicator fields.
        """
        self.df['RSI'] = RSIIndicator(close=self.df.Close, window=window, fillna=fillna).rsi()

        return self.df

    def roc_indicator(self, window: int = 12, fillna: bool = False) -> pd.DataFrame:
        """
        Rate of Change (ROC)
        The Rate-of-Change (ROC) indicator, which is also referred to as simply Momentum, is a pure momentum oscillator
        that measures the percent change in price from one period to the next. The ROC calculation compares the current
        price with the price “n” periods ago. The plot forms an oscillator that fluctuates above and below the zero line
         as the Rate-of-Change moves from positive to negative. As a momentum oscillator, ROC signals include centerline
          crossovers, divergences and overbought-oversold readings. Divergences fail to foreshadow reversals more often
          than not, so this article will forgo a detailed discussion on them. Even though centerline crossovers are
          prone to whipsaw, especially short-term, these crossovers can be used to identify the overall trend.
          Identifying overbought or oversold extremes comes naturally to the Rate-of-Change oscillator.
          https://school.stockcharts.com/doku.php?id=technical_indicators:rate_of_change_roc_and_momentum
        :param window: N -Period.
        :param fillna: If True, fill NaN values.
        :return: DataFrame with ROC indicator field.
        """

        self.df['ROC'] = ROCIndicator(close=self.df.Close, window=window, fillna=fillna).roc()

        return self.df

    def stoch_rsi_indicator(
            self, window: int = 14, smooth1: int = 3, smooth2: int = 3, fillna: bool = False
    ) -> pd.DataFrame:
        """
        Stochastic RSI
        The StochRSI oscillator was developed to take advantage of both momentum indicators in order to create a more
        sensitive indicator that is attuned to a specific security’s historical performance rather than a generalized
        analysis of price change.
        https://school.stockcharts.com/doku.php?id=technical_indicators:stochrsi
        https://www.investopedia.com/terms/s/stochrsi.asp
        :param window: N -Period.
        :param smooth1: Moving average of Stochastic RSI.
        :param smooth2: Moving average of %K.
        :param fillna: If True, fill NaN values.
        :return: DataFrame with Stochastic RSI indicator fields.
        """
        stoch_rsi = StochRSIIndicator(
            close=self.df.Close, window=window, smooth1=smooth1, smooth2=smooth2, fillna=fillna
        )
        self.df['stoch_rsi'] = stoch_rsi.stochrsi()
        self.df['stoch_rsi_d'] = stoch_rsi.stochrsi_d()
        self.df['stoch_rsi_k'] = stoch_rsi.stochrsi_k()

        return self.df

    def stoch_oscillator_indicator(
            self, window: int = 14, smooth_window: int = 3, fillna: bool = False
    ) -> pd.DataFrame:
        """
        Stochastic Oscillator
        Developed in the late 1950s by George Lane. The stochastic oscillator presents the location of the closing
        price of a stock in relation to the high and low range of the price of a stock over a period of time,
        typically a 14-day period.
        https://school.stockcharts.com/doku.php?id=technical_indicators:stochastic_oscillator_fast_slow_and_full
        :param window: N -Period.
        :param smooth_window: SMA period over stoch_k.
        :param fillna: If True, fill NaN values.
        :return: DataFrame with Stochastic Oscillator indicator fileds.
        """
        stochastic_oscillator = StochasticOscillator(
            close=self.df.Close, high=self.df.High, low=self.df.Low, window=window, smooth_window=smooth_window,
            fillna=fillna
        )
        self.df['stoch'] = stochastic_oscillator.stoch()
        self.df['stoch_signal'] = stochastic_oscillator.stoch_signal()

        return self.df

    def all_momentum_indicators(self) -> pd.DataFrame:
        """
        Applies all momentum indicators.
        :return: DataFrame with the all defined momentum indicators.
        """
        self.df = self.rsi_indicator()
        self.df = self.roc_indicator()
        self.df = self.stoch_rsi_indicator()
        self.df = self.stoch_oscillator_indicator()

        return self.df
