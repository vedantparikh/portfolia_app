from typing import List

import yahooquery as yq
import yfinance as yf
import polars as pl

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


def get_symbol_df(name: str, period: str = 'max', interval: str = '1d')->pl.DataFrame:
    ticker = yf.Ticker(name)
    df = ticker.history(period=period, interval=interval)
    # Convert pandas DataFrame to polars DataFrame
    pl_df = pl.from_pandas(df)
    pl_df = pl_df.with_columns(pl.col("index").alias("Datetime"))
    return pl_df


def get_symbol_data(name: str, period: str = 'max', interval: str = '1d')->List[StockData]:
    df = get_symbol_df(name=name, period=period, interval=interval)
    stock_data = [
        StockData(id=d['Datetime'], open=d['Open'],close=d['Close'], low=d['Low'], high=d['High'], volume=d['Volume'], dividends=d['Dividends'])
        for d in df.to_dict(as_series=False)
    ]
    return stock_data

