from typing import List

import yahooquery as yq
import yfinance as yf

from .schemas import Symbol


async def get_symbols(name: str)->List[Symbol]:
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
