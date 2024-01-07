from fastapi import APIRouter

from .momentum_indicators import MomentumIndicators
from market.stock import get_symbol_df

router = APIRouter(prefix='/statistical-indicators', tags=['statistical-indicators'])


@router.get('/momentum-rsi-indicator')
async def rsi_indicator(name: str, period: str = 'max', interval: str = '1d', window: int = 14, fillna: bool = False):
    df = get_symbol_df(name=name, period=period, interval=interval)
    rsi_df = MomentumIndicators(df=df).rsi_indicator(window=window, fillna=fillna)
    """TODO: should be continue in flight"""
    
    return