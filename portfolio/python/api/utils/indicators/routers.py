from fastapi import APIRouter, Depends, Request, HTTPException, status

from .momentum_indicators import MomentumIndicators
from api.v1.market.stock import get_symbol_df
from app.core.auth.dependencies import get_optional_current_user, get_client_ip
from app.core.auth.utils import is_rate_limited

router = APIRouter(prefix="/statistical-indicators", tags=["statistical-indicators"])


@router.get("/momentum-rsi-indicator")
async def rsi_indicator(
    name: str,
    period: str = "max",
    interval: str = "1d",
    window: int = 14,
    fillna: bool = False,
    request: Request = None,
    current_user=Depends(get_optional_current_user),
):
    """
    Calculate RSI (Relative Strength Index) indicator for a symbol.

    Rate limited for unauthenticated users to prevent abuse.
    """
    # Rate limiting for unauthenticated users
    if not current_user:
        client_ip = get_client_ip(request) if request else "unknown"
        if is_rate_limited(
            client_ip, "rsi_indicator", max_attempts=15, window_seconds=3600
        ):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please authenticate or try again later.",
            )

    try:
        df = get_symbol_df(name=name, period=period, interval=interval)
        rsi_df = MomentumIndicators(df=df).rsi_indicator(window=window, fillna=fillna)

        return rsi_df
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error calculating RSI indicator: {str(e)}"
        )
