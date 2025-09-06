import pandas as pd


class BaseIndicator:
    """Base Indicator class."""

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df

        assert not self.df.empty, (
            "No DataFrame was provided to perform the indicator calculation."
        )
