import numpy as np
import pandas as pd
import plotly.graph_objects as go

from trading_strategy.trend_strategy import MACDStrategy


class TrendIndicatorChart:

    def macd_indicator(
            self, df:pd.DataFrame, fig: go, row: int, column: int, window_slow: int = 26, window_fast: int = 12, window_sign: int = 9,
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

        df = MACDStrategy(df=df).buy_sell_strategy()
        df['Hist-Color'] = np.where(df['Histogram'] < 0, 'red', 'green')
        df['MACD-Buy-Sell'] = np.where(df['MACD_buy_or_sell'] < 0, 'green', 'red')
        df.Close = df.Close.round(2)
        df.MACD_price_difference = df.MACD_price_difference.round(2)
        fig.add_trace(
            go.Bar(
                x=df.index, y=df.Histogram, name='Histogram', marker_color=df['Hist-Color'], showlegend=True
            ), row=row, col=column
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df.MACD, name='MACD', line=dict(color='darkorange', width=width),
                text='Close ₹: ' + df['Close'].astype(str) + '<br>Volume : ' + df['Volume'].astype(str),
            ), row=row, col=column
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df.Signal, name='Signal', line=dict(color='cyan', width=width),
                text='Close ₹: ' + df['Close'].astype(str) + '<br>Volume : ' + df['Volume'].astype(str),
            ), row=row, col=column
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df.MACD_buy_or_sell, mode='markers', marker_symbol='triangle-up',
                marker=dict(size=15), marker_color=df['MACD-Buy-Sell'],
                text='Close ₹: ' + df['Close'].astype(str) + '<br>Volume : ' + df['Volume'].astype(str) +
                     '<br>Close diff ₹: ' + df['MACD_price_difference'].astype(str),
            ), row=row, col=column
        )
        fig.update_yaxes(title_text='MACD', row=row, col=column)

        return fig

    def adx_indicator(
            self, df:pd.DataFrame, fig: go, row: int, column: int, window: int = 14, fillna: bool = False, color: str = 'gold',
            width: int = 2,
    ) -> go:
        """
        Creates plot for the ADX indicator.
        :param fig: Plotly go figure.
        :param row: Row number.
        :param column: Column number
        :param window: N -Period.
        :param fillna: If True, fill NaN values.
        :param color: Plot line color.
        :param width: Plot line width.
        :return: Plotly go plot.
        """

        df = df.iloc[window:]
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df.ADX, name='ADX', line=dict(color='green', width=width)
            ), row=row, col=column
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df.ADX_neg, name='ADX -ve', line=dict(color=color, width=width)
            ), row=row, col=column
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df.ADX_pos, name='ADX +ve', line=dict(color='cyan', width=width)
            ), row=row, col=column
        )
        fig.update_yaxes(title_text='ADX', row=row, col=column)

        return fig

    def aroon_indicator(
            self, df:pd.DataFrame, fig: go, row: int, column: int, window: int = 25, fillna: bool = False, color: str = 'gold',
            width: int = 2,
    ) -> go:
        """
        Creates plot for the Aroon indicator.
        :param fig: Plotly go figure.
        :param row: Row number.
        :param column: Column number
        :param window: N -Period.
        :param fillna: If True, fill NaN values.
        :param color: Plot line color.
        :param width: Plot line width.
        :return: Plotly go plot.
        """

        df = df.iloc[window:]
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df.aroon_indicator, name='Aroon', line=dict(color='green', width=width)
            ), row=row, col=column
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df.aroon_up, name='Aroon Up', line=dict(color=color, width=width)
            ), row=row, col=column
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df.aroon_down, name='Aroon Down', line=dict(color='cyan', width=width)
            ), row=row, col=column
        )
        fig.update_yaxes(title_text='Aroon', row=row, col=column)

        return fig

    def psar_indicator(
            self, df:pd.DataFrame, fig: go, row: int, column: int, step: float = 0.02, max_step: float = 0.2, fillna: bool = False,
            color: str = 'gold', width: int = 2,
    ) -> go:
        """
        Creates plot for the Parabolic Stop and Reverse indicator.
        :param fig: Plotly go figure.
        :param row: Row number.
        :param column: Column number
        :param step: Acceleration Factor used to compute the SAR.
        :param max_step: Maximum value allowed for the Acceleration Factor.
        :param fillna: If True, fill NaN values.
        :param color: Plot line color.
        :param width: Plot line width.
        :return: Plotly go plot.
        """

        fig.add_trace(
            go.Scatter(
                x=df.index, y=df.psar, name='PSAR', line=dict(color='green', width=width)
            ), row=row, col=column
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df.psar_down, name='PSAR Down', line=dict(color=color, width=width)
            ), row=row, col=column
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df.psar_up, name='PSAR Up', line=dict(color='cyan', width=width)
            ), row=row, col=column
        )
        fig.update_yaxes(title_text='PSAR', row=row, col=column)

        return fig
