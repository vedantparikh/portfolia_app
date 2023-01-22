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
            symbol.append((quote['symbol'], quote['longname'], quote['quoteType'], quote['exchange']))
        return symbol

keywords = st.text_input('Search by Script name ....')
if keywords:
    matches = get_symbols(keywords)

    if matches:
        symbols = tuple(match[0] for match in matches)
        symbol = st.selectbox('Select the relevant symbol', symbols)
        st.write('You selected:', symbol)
        msft = yf.Ticker(symbol)
        hist = msft.history(period="7d", interval='1m')
        hist['date'] = hist.index
        st.dataframe(hist)

        # https://plotly.com/python/time-series/
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist.index, y=hist.Close))

        fig.update_xaxes(
            rangebreaks=[
                dict(bounds=[15.30, 9.15], pattern="hour"),
                dict(bounds=["sat", "mon"]),
            ]
        )
        st.plotly_chart(fig, use_container_width=True)
