import pandas as pd
from statistical_indicators.momentum_indicators import MomentumIndicators
import yfinance as yf


class GfsStrategy:
    """

    GfsStrategy Class
    -----------------

    This class implements the GFS (Grandfather-Father-Son) strategy for calculating and analyzing relative strength index (RSI) values for a given stock symbol.


    Methods:
    --------

    __init__(self, symbol)
        Initializes an instance of the GfsStrategy class with the given stock symbol.
        If the symbol is not provided, raises a ValueError.

    calculater_rsi(self, df: pd.DataFrame) -> pd.DataFrame
        Calculates the Relative Strength Index (RSI) indicator for each data point in the given DataFrame.

        Parameters:
        - df : pd.DataFrame
          The DataFrame containing the data to calculate RSI indicator for.

        Returns:
        - pd.DataFrame
          The DataFrame with an additional column representing the RSI indicator.

    grandfather_rsi(self)
        Calculates the relative strength index (RSI) using the historical stock data.

        Parameters:
        - self.symbol : str
          The symbol of the stock.

        Returns:
        - float
          The calculated RSI value.

    father_rsi(self)
        Calculates the relative strength index (RSI) using historical stock data.

        Parameters:
        - self : instance of the GfsStrategy class

        Returns:
        - float
          The calculated RSI value.

    son_rsi(self)
        Calculate the RSI (Relative Strength Index) for the given stock symbol.

        Returns:
        - float
          The RSI value.

    calculate_gfs(self) -> dict
        Calculates GFS (Grandfather-Father-Son) strategy.

        Returns:
        - dict
          A dictionary containing calculated RSI values for grandfather, father, and son,
          as well as a recommendation based on the RSI values.
          The dictionary has the following keys:
          - 'grandfather' : float
            RSI value for the grandfather.
          - 'father' : float
            RSI value for the father.
          - 'son' : float
            RSI value for the son.
          - 'recommendation' : str
            Recommendation based on the RSI values ('Buy', 'Sell', or 'Hold Tight! Or Seat Back!').

    """

    def __init__(self, symbol):
        self.symbol = symbol
        if not symbol:
            raise ValueError("Symbol is not present. ")

    def calculater_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates the Relative Strength Index (RSI) indicator for each data point in the given DataFrame.

        Parameters:
        - df: pd.DataFrame
          The DataFrame containing the data to calculate RSI indicator for.

        Returns:
        - pd.DataFrame
          The DataFrame with an additional column representing the RSI indicator.

        """
        return MomentumIndicators(df=df).rsi_indicator()

    def grandfather_rsi(self):
        """
        Calculates the relative strength index (RSI) using the historical stock data.

        Parameters:
        self.symbol (str): The symbol of the stock.

        Returns:
        float: The calculated RSI value.
        """
        stock = yf.Ticker(self.symbol)
        df = stock.history(period="max", interval="1m")
        return self.calculater_rsi(df=df)

    def father_rsi(self):
        """

        Method: father_rsi

        Description:
        This method calculates the relative strength index (RSI) using historical stock data.

        Parameters:
        - self: instance of the GfsStrategy class

        Returns:
        - The calculated RSI value

        """
        stock = yf.Ticker(self.symbol)
        df = stock.history(period="max", interval="5d")
        return self.calculater_rsi(df)

    def son_rsi(self):
        """
        Calculate the RSI (Relative Strength Index) for the given stock symbol.

        :return: The RSI value.
        """
        stock = yf.Ticker(self.symbol)
        df = stock.history(period="max", interval="1d")
        return self.calculater_rsi(df)

    def calculate_gfs(self) -> dict:
        """
        Calculates GFS (Grandfather-Father-Son) strategy.

        Returns:
            dict: A dictionary containing calculated RSI values for grandfather, father, and son,
                  as well as a recommendation based on the RSI values.
                  The dictionary has the following keys:
                  - 'grandfather': RSI value for the grandfather.
                  - 'father': RSI value for the father.
                  - 'son': RSI value for the son.
                  - 'recommendation': Recommendation based on the RSI values ('Buy', 'Sell', or 'Hold Tight! Or Seat Back!').
        """
        grandfather = self.grandfather_rsi()[-1:]["RSI"]
        father = self.father_rsi()[-1:]["RSI"]
        son = self.son_rsi()[-1:]["RSI"]
        result = {
            "grandfather": round(grandfather.to_list()[0], 2),
            "father": round(father.to_list()[0], 2),
            "son": round(son.to_list()[0], 2),
        }

        if grandfather.all() >= 60 and father.all() >= 60 and son.all() >= 40:
            result["recommendation"] = "Buy"
        elif grandfather.all() <= 40 and father.all() <= 40 and son.all() >= 60:
            result["recommendation"] = "Sell"
        else:
            result["recommendation"] = "Hold Tight! Or Seat Back!"
        return result
