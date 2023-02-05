from typing import (
    List,
    Tuple,
)

import plotly.graph_objects as go
import yahooquery as yq
import yfinance as yf
from plotly.subplots import make_subplots

import streamlit as st
from plots import MomentumIndicatorChart

st.set_page_config(page_title='Portfolio', page_icon=':bar_chart:', layout='wide')


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
        quotes = data['quotes']
        if len(quotes) == 0:
            return 'No Symbol Found'

        symbol = []
        for quote in quotes:
            symbol.append((quote['symbol'], quote['quoteType'], quote['exchange']))

        return symbol


keywords = st.text_input('Search by Script name ....')
if keywords:
    matches = get_symbols(keywords)

    if matches:
        symbols = tuple(match[0] for match in matches)
        symbol = st.selectbox('Select the relevant symbol', symbols)
        st.write('You selected:', symbol)
        msft = yf.Ticker(symbol)
        hist = msft.history(period="max", interval='1d')

        fig = make_subplots(
            rows=3, cols=1, shared_xaxes=True, row_heights=[0.5, 0.25, 0.25]
        )
        fig.add_trace(
            go.Candlestick(
                x=hist.index, open=hist.Open, close=hist.Close, low=hist.Low, high=hist.High, showlegend=True,
                name='Close',
            ), row=1, col=1
        )
        fig.add_trace(
            go.Bar(
                x=hist.index, y=hist.Volume, showlegend=True, name='Volume',
            ), row=2, col=1
        )
        fig = MomentumIndicatorChart(df=hist).rsi_indicator_chart(fig=fig, row=3, column=1)
        fig.update_layout(
            autosize=True,
            height=1800,
            xaxis=dict(
                rangeselector=dict(
                    buttons=list(
                        [
                            dict(count=1, label="1m", step="month", stepmode="backward"),
                            dict(count=6, label="6m", step="month", stepmode="backward"),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(count=1, label="1y", step="year", stepmode="backward"),
                            dict(step="all"),
                        ]
                    )
                ),
                rangeslider=dict(visible=False),
                type="date",
            ),
            xaxis2=dict(
                rangeslider=dict(visible=False),
                type="date",
            ),
            xaxis3=dict(
                rangeslider=dict(visible=False),
                type="date",
            ),
        )
        fig.update_xaxes(matches='x')

        st.plotly_chart(fig, use_container_width=True)
