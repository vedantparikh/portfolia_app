from typing import (
    List,
    Tuple,
)

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yahooquery as yq
import yfinance as yf
from plotly.subplots import make_subplots
from ta.momentum import ROCIndicator
from ta.volatility import BollingerBands

from plots import MacdRsiVolumeCandelstickChart

st.set_page_config(page_title='Portfolio', page_icon=':bar_chart:', layout='wide')


def get_symbols(query: str) -> List[Tuple[str, str, str]]:
    """
    Returns the matching tickers and their relevant info.
    @:param query: Query string to look for a ticker.
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


def get_bollinger_theory(df: pd.DataFrame) -> pd.DataFrame:

    indicator_bb = BollingerBands(close=df["Close"], window=20, window_dev=2)

    # Add Bollinger Bands features
    df['bb_bbm'] = indicator_bb.bollinger_mavg()
    df['bb_bbh'] = indicator_bb.bollinger_hband()
    df['bb_bbl'] = indicator_bb.bollinger_lband()

    # Add Bollinger Band high indicator
    df['bb_bbhi'] = indicator_bb.bollinger_hband_indicator()

    # Add Bollinger Band low indicator
    df['bb_bbli'] = indicator_bb.bollinger_lband_indicator()

    return df


keywords = st.text_input('Search by Script name ....')
# keywords = ('SIEMENS.NS')
if keywords:
    matches = get_symbols(keywords)

    if matches:
        symbols = tuple(match[0] for match in matches)
        symbol = st.selectbox('Select the relevant symbol', symbols)
        st.write('You selected:', symbol)
        msft = yf.Ticker(symbol)
        hist = msft.history(period="7d", interval='1m')

        # https://plotly.com/python/time-series/
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist.index, y=hist.Close, texttemplate="%{df.Close[-1]}: <br>(%{df.Close[0]})", ))


        fig.update_xaxes(
            rangebreaks=[
                dict(bounds=[15.15, 9.15], pattern="hour"),
                dict(bounds=["sat", "mon"]),
            ]
        )
        fig.update_layout(
            title="Avg Population: {}".format(hist.Close[0]),
            title_x=0.5,
            xaxis=dict(
                rangeslider=dict(
                    visible=True
                ),
                type="date"
            )
        )
        st.plotly_chart(fig, use_container_width=True)

        hist = msft.history(period="max", interval='1d')
        hist = get_bollinger_theory(hist)
        hist['roci'] = ROCIndicator(hist.Close).roc()
        hist['roci_cumsum'] = hist.roci.cumsum()
        hist['Date'] = hist.index

        # Bollinger chart
        st.text(
            "Some quick observations you can make from looking at this graph "
            "is that the closing prices of the stock mostly stay in between "
            "both the Bollinger bands. "
            "In addition, you can identify buy signals when the price line hits the lower "
            "band and sell signals when the price line hits the higher band.")
        hh = hist[['Date', 'Close', 'bb_bbh', 'bb_bbl']]
        fig = px.line(hh, x='Date', y=hh.columns)
        # fig.add_scatter(hist, x='Date', y=hist.roci_cumsum)
        fig.update_xaxes(
            title_text='Date',
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label='1M', step='month', stepmode='backward'),
                    dict(count=3, label='3M', step='month', stepmode='backward'),
                    dict(count=6, label='6M', step='month', stepmode='backward'),
                    dict(count=1, label='YTD', step='year', stepmode='todate'),
                    dict(count=1, label='1Y', step='year', stepmode='backward'),
                    dict(count=2, label='2Y', step='year', stepmode='backward'),
                    dict(step='all')])))
        st.plotly_chart(fig, use_container_width=True)

        candlesticks = go.Candlestick(
            x=hist.index,
            open=hist['Open'],
            high=hist['High'],
            low=hist['Low'],
            close=hist['Close'],
            showlegend=True
        )

        volume_bars = go.Bar(
            x=hist.index,
            y=hist['Volume'],
            showlegend=False,

        )

        fig = go.Figure(candlesticks)
        fig = make_subplots(specs=[[{
            "secondary_y": True
        }]])
        fig.add_trace(candlesticks, secondary_y=False)
        fig.add_trace(volume_bars, secondary_y=True)
        # fig.add_trace(bb_bbm, secondary_y=True)
        fig.update_yaxes(title="Price", secondary_y=False, showgrid=True)
        fig.update_yaxes(title="Volume", secondary_y=True, showgrid=False)
        fig.update_xaxes(
            rangebreaks=[
                dict(bounds=["sat", "mon"]),
            ]
        )
        st.plotly_chart(fig, use_container_width=True)

        # # Area
        #
        # c_area = go.Scatter(x=hist.index, y=hist.Close, fill='tonexty', hoverinfo='text')
        # fig = go.Figure(c_area)
        # fig = make_subplots(specs=[[{
        #     "secondary_y": True
        # }]])
        # fig.add_trace(c_area, secondary_y=False)
        # fig.add_trace(volume_bars, secondary_y=True)
        #
        # fig.update_xaxes(
        #     title_text='Date',
        #     rangeslider_visible=True,
        #     rangeselector=dict(
        #         buttons=list([
        #             dict(count=1, label='1M', step='month', stepmode='backward'),
        #             dict(count=3, label='3M', step='month', stepmode='backward'),
        #             dict(count=6, label='6M', step='month', stepmode='backward'),
        #             dict(count=1, label='YTD', step='year', stepmode='todate'),
        #             dict(count=1, label='1Y', step='year', stepmode='backward'),
        #             dict(count=2, label='2Y', step='year', stepmode='backward'),
        #             dict(step='all')])))
        #
        # fig.update_yaxes(title_text='Close Price', secondary_y=False, showgrid=True, tickprefix='₹')
        # fig.update_yaxes(title_text='Volume', secondary_y=True, showgrid=False)
        # fig.update_layout(showlegend=False, )
        #
        # st.plotly_chart(fig, use_container_width=True)
        chart = MacdRsiVolumeCandelstickChart().plot(df=hist, ticker=symbol)
        st.plotly_chart(chart, use_container_width=True)