from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from market.routers import router as market_router

app = FastAPI(
    title="Portfolia API",
    description="Financial portfolio analysis and trading strategy API",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(market_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
