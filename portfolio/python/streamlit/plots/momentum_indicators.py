import pandas as pd
import plotly.graph_objects as go


class MomentumIndicatorChart:
    # def __init__(self, df: pd.DataFrame) -> None:
    #     self.df = df
    #
    #     assert not self.df.empty, "No DataFrame was provided to perform the indicator calculation."
    #     self.momentum_indicator = MomentumIndicators(df=df)

    def rsi_indicator_chart(
        self,
        df: pd.DataFrame,
        fig: go,
        row: int,
        column: int,
        window: int = 14,
        fillna: bool = False,
        color: str = "gold",
        width: int = 2,
    ) -> go:
        """
        Creates plot for the RSI indicator.
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
                x=df.index, y=df.RSI, name="RSI", line=dict(color=color, width=width)
            ),
            row=row,
            col=column,
        )
        fig.update_yaxes(title_text="RSI", row=row, col=column)

        return fig

    def roc_indicator_chart(
        self,
        df: pd.DataFrame,
        fig: go,
        row: int,
        column: int,
        window: int = 12,
        fillna: bool = False,
        color: str = "gold",
        width: int = 2,
    ) -> go:
        """
        Creates plot for the ROC indicator.
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
                x=df.index, y=df.ROC, name="ROC", line=dict(color=color, width=width)
            ),
            row=row,
            col=column,
        )
        fig.update_yaxes(title_text="ROC", row=row, col=column)

        return fig

    def stoch_rsi_indicator_chart(
        self,
        df: pd.DataFrame,
        fig: go,
        row: int,
        column: int,
        window: int = 14,
        smooth1: int = 3,
        smooth2: int = 3,
        fillna: bool = False,
        color: str = "gold",
        width: int = 2,
    ) -> go:
        """
        Creates plot for the Stochastic RSI indicator.
        :param fig: Plotly go figure.
        :param row: Row number.
        :param column: Column number
        :param window: N -Period.
        :param smooth1: Moving average of Stochastic RSI.
        :param smooth2: Moving average of %K.
        :param fillna: If True, fill NaN values.
        :param color: Plot line color.
        :param width: Plot line width.
        :return: Plotly go plot.
        """

        df = df.iloc[window:]
        fig.add_trace(
            # TODO: multiple fields.
            go.Scatter(
                x=df.index,
                y=df.stoch_rsi,
                name="Stochastic RSI",
                line=dict(color=color, width=width),
            ),
            row=row,
            col=column,
        )
        fig.update_yaxes(title_text="Stochastic RSI", row=row, col=column)

        return fig

    def stoch_oscillator_indicator_chart(
        self,
        df: pd.DataFrame,
        fig: go,
        row: int,
        column: int,
        window: int = 14,
        smooth_window: int = 3,
        fillna: bool = False,
        color: str = "gold",
        width: int = 2,
    ) -> go:
        """
        Creates plot for the Stochastic Oscillator indicator.
        :param fig: Plotly go figure.
        :param row: Row number.
        :param column: Column number
        :param window: N -Period.
        :param smooth_window: SMA period over stoch_k.
        :param fillna: If True, fill NaN values.
        :param color: Plot line color.
        :param width: Plot line width.
        :return: Plotly go plot.
        """

        df = df.iloc[window:]
        fig.add_trace(
            # TODO: multiple fields.
            go.Scatter(
                x=df.index,
                y=df.stoch,
                name="Stochastic Oscillator",
                line=dict(color=color, width=width),
            ),
            row=row,
            col=column,
        )
        fig.update_yaxes(title_text="Stochastic Oscillator", row=row, col=column)

        return fig
