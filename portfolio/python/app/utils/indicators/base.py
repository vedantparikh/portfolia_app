import polars as pl


class BaseIndicator:
    """Base Indicator class."""

    def __init__(self, df: pl.DataFrame) -> None:
        self.df = df

        assert not self.df.is_empty(), (
            "No DataFrame was provided to perform the indicator calculation."
        )
