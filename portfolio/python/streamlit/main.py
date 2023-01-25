import streamlit as st
import yahooquery as yq
import yfinance as yf
import plotly.graph_objects as go

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
keywords = ('SIEMENS.NS')
if keywords:
    matches = get_symbols(keywords)
    matches = 'SIEMENS.NS'

    if matches:
        symbols = tuple(match[0] for match in matches)
        symbol = st.selectbox('Select the relevant symbol', symbols)
        st.write('You selected:', symbol)
        msft = yf.Ticker(symbol)
        hist = msft.history(period="max", interval='1d')
        st.dataframe(hist)

        # https://plotly.com/python/time-series/
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist.index, y=hist.Close))

        fig.update_xaxes(
            rangebreaks=[
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

        hist = msft.history(period="7d", interval='1m')
        st.dataframe(hist)
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


        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        candlesticks = go.Candlestick(
            x=hist.index,
            open=hist['Open'],
            high=hist['High'],
            low=hist['Low'],
            close=hist['Close'],
            showlegend=False
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
        fig.update_layout(title="ETH/USDC pool after Uniswap v3 deployment", height=800)
        fig.update_yaxes(title="Price $", secondary_y=False, showgrid=True)
        fig.update_yaxes(title="Volume $", secondary_y=True, showgrid=False)
        fig.update_xaxes(
            rangebreaks=[
                dict(bounds=[15.15, 9.15], pattern="hour"),
                dict(bounds=["sat", "mon"]),
            ]
        )
        st.plotly_chart(fig, use_container_width=True)