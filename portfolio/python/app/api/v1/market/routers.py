from fastapi import APIRouter

from .data_router import router as data_router
from .stock import router as stock_router

router = APIRouter()

# Include stock router
router.include_router(stock_router, prefix="/stock")

# Include market data router
router.include_router(data_router)
