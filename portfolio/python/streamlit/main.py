import os
import requests
from pprint import pprint
from alpha_vantage.timeseries import TimeSeries  # https://pypi.org/project/alpha-vantage/
import yfinance as yf
import streamlit as st

API_KEY = os.getenv('API_KEY')
st.title('Portfolio App')

API_KEY = 'T60Q1RPYX7I7MONU'

keywords = st.text_input('Search by Script name ....')
if keywords:
    search_url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={keywords}&apikey={API_KEY}'
    r = requests.get(search_url)
    data = r.json()
    print(data)
    matches = data.get('bestMatches')
    if matches:
        symbols = tuple(match['1. symbol'] for match in matches)
        symbol= st.selectbox('Select the relevant symbol', symbols)
        st.write('You selected:', symbol)
        print(symbol)
        u = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={API_KEY}&outputsize=full'
        r = requests.get(u)
        data = r.json()
        print(data)
        st.json(data)
        # # # ts = TimeSeries(key='T59Q1RPYX7I7MONU',output_format='pandas', indexing_type='date')
        # data, meta_data = ts.get_intraday(symbol=symbol,interval='1min', outputsize='full')
        # pprint(data.head(2))
    # st.json(data)



#ts = TimeSeries(key='T59Q1RPYX7I7MONU',output_format='pandas', indexing_type='date')
#data, meta_data = ts.get_intraday(symbol='MSFT',interval='1min', outputsize='full')
#pprint(data.head(2))
#st.text_area(data)