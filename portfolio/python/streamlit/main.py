import os
import requests
from pprint import pprint

from alpha_vantage.timeseries import TimeSeries  # https://pypi.org/project/alpha-vantage/
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
    st.json(data)
    matches = data.get('bestMatches')
    if matches:
        symbols = tuple(match['1. symbol'] for match in matches)
        symbol= st.selectbox('Select the relevant symbol', symbols)
        st.write('You selected:', symbol)
        u = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=SIEMENS&interval=5min&apikey={API_KEY}'
        r = requests.get(u)
        data = r.json()
        st.json(data)