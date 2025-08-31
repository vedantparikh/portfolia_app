import polars as pl
import yfinance as yf

from utils.indicators.momentum_indicators import MomentumIndicators


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

    calculater_rsi(self, df: pl.DataFrame) -> pl.DataFrame
        Calculates the Relative Strength Index (RSI) indicator for each data point in the given DataFrame.

        Parameters:
        - df : pl.DataFrame
          The DataFrame containing the data to calculate RSI indicator for.

        Returns:
        - pl.DataFrame
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
          The RSI value.

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

    def calculater_rsi(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Calculates the Relative Strength Index (RSI) indicator for each data point in the given DataFrame.

        Parameters:
        - df: pl.DataFrame
          The DataFrame containing the data to calculate RSI indicator for.

        Returns:
        - pl.DataFrame
          The DataFrame with an additional column representing the RSI indicator.

        """
        return MomentumIndicators(df=df).rsi_indicator()

    def grandfather_rsi(self):
        """
        Calculates the relative strength index (RSI) using the historical stock data.

        Parameters:
        - self.symbol : str
          The symbol of the stock.

        Returns:
        - float
          The calculated RSI value.

        """
        try:
            ticker = yf.Ticker(self.symbol)
            df = ticker.history(period="5y", interval="1d")
            if df.empty:
                raise ValueError(
                    f"{self.symbol}: No price data found, symbol may be delisted (period=5y)"
                )

            # Convert to polars DataFrame
            pl_df = pl.from_pandas(df)
            return self.calculater_rsi(df=pl_df)
        except Exception as e:
            raise ValueError(
                f"{self.symbol}: No price data found, symbol may be delisted (period=5y)"
            )

    def father_rsi(self):
        """
        Calculates the relative strength index (RSI) using historical stock data.

        Parameters:
        - self : instance of the GfsStrategy class

        Returns:
        - float
          The RSI value.

        """
        try:
            ticker = yf.Ticker(self.symbol)
            df = ticker.history(period="1y", interval="1d")
            if df.empty:
                raise ValueError(
                    f"{self.symbol}: No price data found, symbol may be delisted (period=1y)"
                )

            # Convert to polars DataFrame
            pl_df = pl.from_pandas(df)
            return self.calculater_rsi(df=pl_df)
        except Exception as e:
            raise ValueError(
                f"{self.symbol}: No price data found, symbol may be delisted (period=1y)"
            )

    def son_rsi(self):
        """
        Calculate the RSI (Relative Strength Index) for the given stock symbol.

        Returns:
        - float
          The RSI value.

        """
        try:
            ticker = yf.Ticker(self.symbol)
            df = ticker.history(period="1mo", interval="1d")
            if df.empty:
                raise ValueError(
                    f"{self.symbol}: No price data found, symbol may be delisted (period=1mo)"
                )

            # Convert to polars DataFrame
            pl_df = pl.from_pandas(df)
            return self.calculater_rsi(df=pl_df)
        except Exception as e:
            raise ValueError(
                f"{self.symbol}: No price data found, symbol may be delisted (period=1mo)"
            )

    def calculate_gfs(self) -> dict:
        """
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
        try:
            grandfather = self.grandfather_rsi()
            father = self.father_rsi()
            son = self.son_rsi()

            # Extract the last RSI value from each DataFrame
            grandfather_rsi = grandfather.select("RSI").tail(1).item()
            father_rsi = father.select("RSI").tail(1).item()
            son_rsi = son.select("RSI").tail(1).item()

            # Determine recommendation based on RSI values
            if grandfather_rsi < 30 and father_rsi < 30 and son_rsi < 30:
                recommendation = "Buy"
            elif grandfather_rsi > 70 and father_rsi > 70 and son_rsi > 70:
                recommendation = "Sell"
            else:
                recommendation = "Hold Tight! Or Seat Back!"

            return {
                "grandfather": grandfather_rsi,
                "father": father_rsi,
                "son": son_rsi,
                "recommendation": recommendation,
            }
        except Exception as e:
            raise ValueError(f"Error calculating GFS strategy: {str(e)}")
