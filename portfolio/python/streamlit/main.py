import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yahooquery as yq
import yfinance as yf
from plotly.subplots import make_subplots

st.title('Portfolio App')

def get_symbols(query):
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
        fig.add_trace(go.Scatter(x=hist.index, y=hist.Close))

        fig.update_xaxes(
            rangebreaks=[
                dict(bounds=[15.15, 9.15], pattern="hour"),
                dict(bounds=["sat", "mon"]),
            ]
        )
        fig.update_layout(
            xaxis=dict(
                rangeslider=dict(
            visible=True
        ),
        type="date"
            )
        )
        st.plotly_chart(fig, use_container_width=True)

        hist = msft.history(period="max", interval='1d')
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
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(candlesticks, secondary_y=False)
        fig.add_trace(volume_bars, secondary_y=True)
        fig.update_yaxes(title="Price", secondary_y=False, showgrid=True)
        fig.update_yaxes(title="Volume", secondary_y=True, showgrid=False)
        fig.update_xaxes(
            rangebreaks=[
                dict(bounds=["sat", "mon"]),
            ]
        )
        st.plotly_chart(fig, use_container_width=True)

        c_area = px.area(hist.Close, title='FACBOOK SHARE PRICE (2013-2020)')

        c_area.update_xaxes(
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

        c_area.update_yaxes(title_text='Close Price', tickprefix='₹')
        c_area.update_layout(showlegend=False,)

        st.plotly_chart(c_area, use_container_width=True)