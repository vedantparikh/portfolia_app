from fastapi import APIRouter

from .stock import get_symbols, get_symbol_data

router = APIRouter(prefix='/market', tags=['market-data'])


@router.get('/symbols')
async def symbols(name: str):

    return get_symbols(name=name)


@router.get('/symbol-data')
async def symbol_data(name: str, period: str = 'max', interval: str = '1d'):
    return get_symbol_data(name=name, period=period, interval=interval)
