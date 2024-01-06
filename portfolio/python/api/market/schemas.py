from pydantic import BaseModel


class Symbol(BaseModel):
    symbol: str
    quoteType: str