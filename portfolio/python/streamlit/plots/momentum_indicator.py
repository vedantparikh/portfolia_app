import pandas as pd
import plotly.graph_objects as go

from streamlit.statistical_indicators import MomentumIndicators


class MomentumIndicatorChart:
    def __int__(self, df: pd.DataFrame) -> None:
        self.df = df

        assert not self.df.empty, "No DataFrame was provided to perform the indicator calculation."
        self.momentum_indicator = MomentumIndicators(df=df)

    def rsi_indicator_chart(
            self, fig: go, row: int, column: int, window: int = 14, fillna: bool = False, color: str = 'gold',
            width: int = 2
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

        df = self.momentum_indicator.rsi_indicator(window=window, fillna=fillna)
        fig.add_trace(
            go.Scatter(
                x=df.index.iloc[window:], y=df.RSI.iloc[window:], name='RSI', line=dict(color=color, width=width)
            ),
            row=row, col=column
        )
        fig.update_yaxes(title_text='RSI', row=row, col=column)

        return fig
