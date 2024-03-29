import pandas as pd
import plotly.graph_objects as go


class VolumeIndicatorChart:

    def mfi_indicator(
            self, df: pd.DataFrame, fig: go, row: int, column: int, window: int = 14, fillna: bool = False,
            color: str = 'gold',
            width: int = 2
    ) -> go:
        """
        Creates plot for the MFI indicator.
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
                x=df.index, y=df.mfi_indicator, name='MFI', line=dict(color=color, width=width)
            ),
            row=row, col=column
        )
        fig.update_yaxes(title_text='MFI', row=row, col=column)

        return fig

    def volume_price_trend_indicator(
            self, df: pd.DataFrame, fig: go, row: int, column: int, fillna: bool = False, color: str = 'gold', width: int = 2
    ) -> go:
        """
        Creates plot for the Volume price trend indicator.
        :param fig: Plotly go figure.
        :param row: Row number.
        :param column: Column number
        :param fillna: If True, fill NaN values.
        :param color: Plot line color.
        :param width: Plot line width.
        :return: Plotly go plot.
        """

        fig.add_trace(
            go.Scatter(
                x=df.index, y=df.volume_price_trend, name='Volume Price Trend', line=dict(color=color, width=width)
            ),
            row=row, col=column
        )
        fig.update_yaxes(title_text='Volume Price Trend', row=row, col=column)

        return fig

    def volume_weighted_average_price(
            self, df: pd.DataFrame, fig: go, row: int, column: int, window: int = 14, fillna: bool = False, color: str = 'gold',
            width: int = 2
    ) -> go:
        """
        Creates plot for the Volume price trend indicator.
        :param fig: Plotly go figure.
        :param row: Row number.
        :param column: Column number
        :param window: N -Period.
        :param fillna: If True, fill NaN values.
        :param color: Plot line color.
        :param width: Plot line width.
        :return: Plotly go plot.
        """

        fig.add_trace(
            go.Scatter(
                x=df.index, y=df.volume_weighted_average_price, name='Volume Weighted Average Price',
                line=dict(color=color, width=width)
            ),
            row=row, col=column
        )
        fig.update_yaxes(title_text='Volume Weighted Average Price', row=row, col=column)

        return fig

    def on_balance_volume_indicator(
            self, df: pd.DataFrame, fig: go, row: int, column: int, fillna: bool = False, color: str = 'gold', width: int = 2
    ) -> go:
        """
        Creates plot for the On Balance Volume indicator.
        :param fig: Plotly go figure.
        :param row: Row number.
        :param column: Column number
        :param fillna: If True, fill NaN values.
        :param color: Plot line color.
        :param width: Plot line width.
        :return: Plotly go plot.
        """

        fig.add_trace(
            go.Scatter(
                x=df.index, y=df.on_balance_volume, name='On Balance Volume', line=dict(color=color, width=width)
            ),
            row=row, col=column
        )
        fig.update_yaxes(title_text='On Balance Volume', row=row, col=column)

        return fig

    def force_index_indicator(
            self, df: pd.DataFrame, fig: go, row: int, column: int, window: int = 13, fillna: bool = False, color: str = 'gold',
            width: int = 2
    ) -> go:
        """
        Creates plot for the Force Index (FI) indicator.
        :param fig: Plotly go figure.
        :param row: Row number.
        :param column: Column number
        :param window: N -Period.
        :param fillna: If True, fill NaN values.
        :param color: Plot line color.
        :param width: Plot line width.
        :return: Plotly go plot.
        """

        fig.add_trace(
            go.Scatter(
                x=df.index, y=df.force_index, name='Force Index (FI)',
                line=dict(color=color, width=width)
            ),
            row=row, col=column
        )
        fig.update_yaxes(title_text='Force Index (FI)', row=row, col=column)

        return fig
