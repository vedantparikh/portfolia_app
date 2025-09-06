import pandas as pd
from statistical_indicators.base import BaseIndicator
from ta.volume import (
    ForceIndexIndicator,
    MFIIndicator,
    OnBalanceVolumeIndicator,
    VolumePriceTrendIndicator,
    VolumeWeightedAveragePrice,
)


class VolumeIndicators(BaseIndicator):
    """Returns a Pandas Dataframe with calculated different Volume Indicators."""

    def mfi_indicator(self, window: int = 14, fillna: bool = False) -> pd.DataFrame:
        """
        Money Flow Index (MFI)
        Uses both price and volume to measure buying and selling pressure. It is positive when the typical price rises
        (buying pressure) and negative when the typical price declines (selling pressure). A ratio of positive and
        negative money flow is then plugged into an RSI formula to create an oscillator that moves between zero and
        one hundred.
        http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:money_flow_index_mfi
        :param window: N -Period.
        :param fillna: If True, fill NaN values.
        :return: DataFrame with the MFI indicator fields.
        """
        self.df["mfi_indicator"] = MFIIndicator(
            high=self.df.High,
            low=self.df.Low,
            close=self.df.Close,
            volume=self.df.Volume,
            window=window,
            fillna=fillna,
        ).money_flow_index()

        return self.df

    def volume_price_trend_indicator(self, fillna: bool = False) -> pd.DataFrame:
        """
        Volume-price trend (VPT)
        Is based on a running cumulative volume that adds or subtracts a multiple of the percentage change in share
        price trend and current volume, depending upon the investment’s upward or downward movements.
        https://en.wikipedia.org/wiki/Volume%E2%80%93price_trend
        :param fillna: If True, fill NaN values.
        :return: DataFrame with the volume price trend indicator fields.
        """
        self.df["volume_price_trend"] = VolumePriceTrendIndicator(
            close=self.df.Close, volume=self.df.Volume, fillna=fillna
        ).volume_price_trend()

        return self.df

    def volume_weighted_average_price(
        self, window: int = 14, fillna: bool = False
    ) -> pd.DataFrame:
        """
        Volume Weighted Average Price (VWAP)
        VWAP equals the dollar value of all trading periods divided by the total trading volume for the current day.
        The calculation starts when trading opens and ends when it closes. Because it is good for the current trading
        day only, intraday periods and data are used in the calculation.
        https://school.stockcharts.com/doku.php?id=technical_indicators:vwap_intraday
        :param window: N -Period.
        :param fillna: If True, fill NaN values.
        :return: DataFrame with the volume weighted average price field.
        """
        self.df["volume_weighted_average_price"] = VolumeWeightedAveragePrice(
            high=self.df.High,
            low=self.df.Low,
            close=self.df.Close,
            volume=self.df.Volume,
            window=window,
            fillna=fillna,
        ).volume_weighted_average_price()

        return self.df

    def on_balance_volume_indicator(self, fillna: bool = False) -> pd.DataFrame:
        """

        :param fillna:
        :return:
        """
        self.df["on_balance_volume"] = OnBalanceVolumeIndicator(
            close=self.df.Close, volume=self.df.Volume, fillna=fillna
        ).on_balance_volume()

        return self.df

    def force_index_indicator(
        self, window: int = 13, fillna: bool = False
    ) -> pd.DataFrame:
        """
        Force Index (FI)
        It illustrates how strong the actual buying or selling pressure is. High positive values mean there is a
        strong rising trend, and low values signify a strong downward trend.
        http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:force_index
        :param window: N -Period.
        :param fillna: If True, fill NaN values.
        :return: DataFrame with the FI indicator field.
        """
        self.df["force_index"] = ForceIndexIndicator(
            close=self.df.Close, volume=self.df.Volume, window=window, fillna=fillna
        ).force_index()

        return self.df

    def all_volume_indicators(self) -> pd.DataFrame:
        """
        Applies all volume indicators.
        :return: DataFrame with the all defined volume indicators.
        """

        self.df = self.mfi_indicator()
        self.df = self.volume_price_trend_indicator()
        self.df = self.volume_weighted_average_price()
        self.df = self.on_balance_volume_indicator()
        self.df = self.force_index_indicator()

        return self.df
