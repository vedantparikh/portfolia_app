from concurrent.futures import ProcessPoolExecutor
from typing import (
    List,
    Tuple,
)

import plotly.graph_objects as go
import yahooquery as yq
import yfinance as yf
from plotly.subplots import make_subplots
from plots import MomentumIndicatorChart, TrendIndicatorChart, VolatilityIndicatorChart
from statistical_indicators import (
    MomentumIndicators,
    TrendIndicators,
    VolatilityIndicators,
)
from trading_strategy.trend_strategy.gfs_strategy.gfs import GfsStrategy

import streamlit as st

st.set_page_config(page_title="Portfolio", page_icon=":bar_chart:", layout="wide")


def get_symbols(query: str) -> List[Tuple[str, str, str]]:
    """
    Returns the matching tickers and their relevant info.
    :param query: Query string to look for a ticker.
    """
    try:
        data = yq.search(query)
    except ValueError:
        print(query)
    else:
        quotes = data["quotes"]
        if len(quotes) == 0:
            return "No Symbol Found"

        symbol = []
        for quote in quotes:
            symbol.append((quote["symbol"], quote["quoteType"], quote["exchange"]))

        return symbol


keywords = st.text_input("Search by Script name ....")
if keywords:
    matches = get_symbols(keywords)

    if matches:
        symbols = tuple(match[0] for match in matches)
        symbol = st.selectbox("Select the relevant symbol", symbols)
        st.write("You selected:", symbol)
        msft = yf.Ticker(symbol)
        hist = msft.history(period="max", interval="1d")

        fig = make_subplots(
            rows=5, cols=1, shared_xaxes=True, row_heights=[0.4, 0.1, 0.1, 0.1, 0.3]
        )
        fig.add_trace(
            go.Candlestick(
                x=hist.index,
                open=hist.Open,
                close=hist.Close,
                low=hist.Low,
                high=hist.High,
                showlegend=True,
                name="Candle",
            ),
            row=1,
            col=1,
        )
        fig.update_layout(
            autosize=True,
            height=1000,
            yaxis=dict(autorange=True, fixedrange=False),
            xaxis=dict(
                rangeselector=dict(
                    buttons=list(
                        [
                            dict(
                                count=1, label="1m", step="month", stepmode="backward"
                            ),
                            dict(
                                count=3, label="3m", step="month", stepmode="backward"
                            ),
                            dict(
                                count=6, label="6m", step="month", stepmode="backward"
                            ),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(count=1, label="1Y", step="year", stepmode="backward"),
                            dict(count=2, label="2Y", step="year", stepmode="backward"),
                            dict(label="All", step="all"),
                        ]
                    )
                ),
                rangeslider=dict(visible=False),
                type="date",
            ),
        )
        with ProcessPoolExecutor() as executor:
            # execute the task
            future_gfs = executor.submit(GfsStrategy(symbol=symbol).calculate_gfs)
            future_rsi = executor.submit(MomentumIndicators(df=hist).rsi_indicator)
            future_roc = executor.submit(MomentumIndicators(df=hist).roc_indicator)
            future_macd = executor.submit(TrendIndicators(df=hist).macd_indicator)
            future_bollinger = executor.submit(
                VolatilityIndicators(df=hist).bollinger_bands_indicator
            )

            gfs = future_gfs.result()
            rsi = future_rsi.result()
            roc = future_roc.result()
            macd = future_macd.result()
            bollinger = future_bollinger.result()

        fig.add_annotation(
            text=f"GFS Strategy:<br> Grandfather: {gfs['grandfather']}<br> Father: {gfs['father']}<br> Son: {gfs['son']} "
            f"<br> Recommendation: {gfs['recommendation']}",
            align="left",
            showarrow=False,
            xref="paper",
            yref="paper",
            x=1.1,
            y=0.8,
            bordercolor="black",
            borderwidth=1,
        )
        fig.add_trace(
            go.Bar(
                x=hist.index,
                y=hist.Volume,
                showlegend=True,
                name="Volume",
            ),
            row=2,
            col=1,
        )
        fig.update_layout(
            xaxis2=dict(
                rangeslider=dict(visible=False),
                type="date",
            ),
            yaxis2=dict(autorange=True, fixedrange=False),
        )
        fig = MomentumIndicatorChart().rsi_indicator_chart(
            df=rsi, fig=fig, row=3, column=1
        )
        fig.update_layout(
            xaxis3=dict(
                rangeslider=dict(visible=False),
                type="date",
            ),
            yaxis3=dict(autorange=True, fixedrange=False),
        )
        fig = MomentumIndicatorChart().roc_indicator_chart(
            df=roc, fig=fig, row=4, column=1
        )
        fig.update_layout(
            xaxis4=dict(
                rangeslider=dict(visible=False),
                type="date",
            ),
            yaxis4=dict(autorange=True, fixedrange=False),
        )
        fig = TrendIndicatorChart().macd_indicator(df=macd, fig=fig, row=5, column=1)
        fig.update_layout(
            xaxis5=dict(
                rangeslider=dict(visible=False),
                type="date",
            ),
            yaxis5=dict(autorange=True, fixedrange=False),
        )
        fig = VolatilityIndicatorChart().bollinger_bands_indicator(
            df=bollinger, fig=fig, row=1, column=1
        )

        fig.update_xaxes(matches="x")

        st.plotly_chart(fig, use_container_width=True)
