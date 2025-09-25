import pandas as pd
import polars as pl


class BaseIndicator:
    """Base Indicator class with pythonic column naming."""

    def __init__(self, df) -> None:
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
                raise TypeError(
                    "Input 'df' is not a Polars DataFrame and pandas is not installed for conversion."
                )

        # Normalize column names to pythonic snake_case
        self.df = self._normalize_column_names(self.df)

        # Updated the assertion to use the idiomatic Polars `is_empty()` method
        assert (
            not self.df.is_empty()
        ), "The DataFrame is empty. No indicator calculation can be performed."

    def _normalize_column_names(self, df: pl.DataFrame) -> pl.DataFrame:
        """Convert column names to pythonic snake_case."""
        column_mapping = {
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
            "Adj Close": "adj_close",
        }

        # Apply column name mapping
        rename_dict = {}
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                rename_dict[old_name] = new_name

        if rename_dict:
            df = df.rename(rename_dict)

        return df
