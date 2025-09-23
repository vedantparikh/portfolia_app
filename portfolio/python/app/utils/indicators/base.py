import polars as pl
import pandas as pd


class BaseIndicator:
    """Base Indicator class."""

    def __init__(self, df) -> None:  # Removed the strict pl.DataFrame type hint

        # Check if it's already a Polars DataFrame
        if isinstance(df, pl.DataFrame):
            self.df = df
        else:
            # Try to import pandas and check if it's a pandas DataFrame
            try:
                if isinstance(df, pd.DataFrame):
                    # Convert pandas DataFrame to Polars DataFrame
                    self.df = pl.from_pandas(df)
                else:
                    # If it's not pandas or polars, raise an error
                    raise TypeError("Input 'df' must be a Polars or pandas DataFrame.")
            except ImportError:
                # This catches the case where pandas is not installed
                raise TypeError("Input 'df' is not a Polars DataFrame and pandas is not installed for conversion.")

        # Updated the assertion to use the idiomatic Polars `is_empty()` method
        assert not self.df.is_empty(), (
            "The DataFrame is empty. No indicator calculation can be performed."
        )
