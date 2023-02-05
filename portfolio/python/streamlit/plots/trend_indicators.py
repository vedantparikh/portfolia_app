import numpy as np
import pandas as pd
import plotly.graph_objects as go

from statistical_indicators import TrendIndicators


class TrendIndicatorChart:
    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df

        assert not self.df.empty, "No DataFrame was provided to perform the indicator calculation."
        self.trend_indicator = TrendIndicators(df=df)

    def macd_indicator(
            self, fig: go, row: int, column: int, window_slow: int = 26, window_fast: int = 12, window_sign: int = 9,
            fillna: bool = False, color: str = 'gold', width: int = 2,
    ) -> go:
        """
        Creates plot for the MACD indicator.
        :param fig: Plotly go figure.
        :param row: Row number.
        :param column: Column number
        :param window_slow: N -Period long term.
        :param window_fast: N -Period short term.
        :param window_sign: N -Period to signal.
        :param fillna: If True, fill NaN values.
        :param color: Plot line color.
        :param width: Plot line width.
        :return: Plotly go plot.
        """

        df = self.trend_indicator.macd_indicator(
            window_slow=window_slow, window_fast=window_fast, fillna=fillna, window_sign=window_sign,
        )
        df['Hist-Color'] = np.where(df['Histogram'] < 0, 'red', 'green')
        fig.add_trace(
            go.Bar(
                x=df.index, y=df.Histogram, name='Histogram', marker_color=df['Hist-Color'], showlegend=True
            ), row=row, col=column
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df.MACD, name='MACD', line=dict(color='darkorange', width=2)
            ), row=row, col=column
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df.Signal, name='Signal', line=dict(color='cyan', width=2)
            ), row=row, col=column
        )
        fig.update_yaxes(title_text='MACD', row=row, col=column)

        return fig
