import os

import streamlit as st
from alpha_vantage.timeseries import TimeSeries  # https://pypi.org/project/alpha-vantage/

API_KEY = os.getenv('API_KEY')
st.title('Portfolio App')

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
search_url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=tesco&apikey={API_KEY}'

ts = TimeSeries(key='T59Q1RPYX7I7MONU', output_format='pandas')
data, meta_data = ts.get_intraday(symbol='MSFT', interval='1min', outputsize='full')

st.table(data)
