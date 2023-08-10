import pandas as pd
import plotly.graph_objects as go


class VolatilityIndicatorChart:

    def bollinger_bands_indicator(
            self, df: pd.DataFrame, fig: go, row: int, column: int, window: int = 20, window_dev: int = 2,
            fillna: bool = False,
            color: str = 'gold', width: int = 2,
    ) -> go:
        """
        Creates plot for the Bollinger Bands indicator.
        :param fig: Plotly go figure.
        :param row: Row number.
        :param column: Column number
        :param window: N -period.
        :param window_dev: N -factor standard deviation
        :param fillna: If True, fill NaN values.
        :param color: Plot line color.
        :param width: Plot line width.
        :return: Plotly go plot.
        """

        df = df.iloc[window:]
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df.bb_bbm, name='Bollinger MAVG', line=dict(color='green', width=width)
            ), row=row, col=column
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df.bb_bbh, name='Bollinger hband', line=dict(color=color, width=width)
            ), row=row, col=column
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df.bb_bbl, name='Bollinger lband', line=dict(color='cyan', width=width)
            ), row=row, col=column
        )
        fig.update_yaxes(title_text='Bollinger Bands', row=row, col=column)

        return fig

    def average_true_range_indicator(
            self, df: pd.DataFrame, fig: go, row: int, column: int, window: int = 20, fillna: bool = False,
            color: str = 'gold',
            width: int = 2,
    ) -> go:
        """
        Creates plot for the Average True Range indicator.
        :param fig: Plotly go figure.
        :param row: Row number.
        :param column: Column number
        :param window: N -period.
        :param fillna: If True, fill NaN values.
        :param color: Plot line color.
        :param width: Plot line width.
        :return: Plotly go plot.
        """

        df = df.iloc[window:]
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df.average_true_range, name='Average True Range', line=dict(color='green', width=width)
            ), row=row, col=column
        )
        fig.update_yaxes(title_text='Average True Range', row=row, col=column)

        return fig

    def keltner_channel_indicator(
            self, df: pd.DataFrame, fig: go, row: int, column: int, window: int = 20, window_atr: int = 10,
            original_version: bool = True,
            multiplier: int = 2, fillna: bool = False, color: str = 'gold', width: int = 2,
    ) -> go:
        """
        Creates plot for the Keltner Channel indicator.
        :param fig: Plotly go figure.
        :param row: Row number.
        :param column: Column number
        :param window: N -period.
        :param window_atr: N atr period. Only valid if original_version param is False.
        :param original_version: If True, use original version as the centerline (SMA of typical price) if False,
        use EMA of close as the centerline. More info:
        https://school.stockcharts.com/doku.php?id=technical_indicators:keltner_channels
        :param multiplier: The multiplier has the most effect on the channel width. default is 2
        :param fillna: If True, fill NaN values.
        :param color: Plot line color.
        :param width: Plot line width.
        :return: Plotly go plot.
        """

        df = df.iloc[window:]
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df.keltner_channel_mband, name='Keltner Channel mband',
                line=dict(color='green', width=width)
            ), row=row, col=column
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df.keltner_channel_hband, name='Keltner Channel hband',
                line=dict(color=color, width=width)
            ), row=row, col=column
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df.keltner_channel_lband, name='Keltner Channel lband',
                line=dict(color='cyan', width=width)
            ), row=row, col=column
        )
        fig.update_yaxes(title_text='Keltner Channel', row=row, col=column)

        return fig
