from typing import List

import yahooquery as yq
import yfinance as yf

from .schemas import Symbol, StockData


def get_symbols(name: str) -> List[Symbol]:
    """
    Returns the matching tickers and their relevant info.
    :param qame: Name string to look for a ticker.
    """
    data = yq.search(name)
    quotes = data['quotes']
    if len(quotes) == 0:
        return 'No Symbol Found'
    symbols = [
        Symbol(symbol=str(qoute['symbol']), quoteType=str(qoute['quoteType']))
        for qoute in quotes
    ]

    return symbols


def get_symbol_data(name: str, period: str = 'max', interval: str = '1d')->List[StockData]:
    ticker = yf.Ticker(name)
    data = ticker.history(period=period, interval=interval)
    data['Datetime'] = data.index
    stock_data = [
        StockData(id=d['Datetime'], open=d['Open'],close=d['Close'], low=d['Low'], high=d['High'], volume=d['Volume'], dividends=d['Dividends'])
        for d in data.to_dict('records')
    ]
    return stock_data
