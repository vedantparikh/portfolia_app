from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn

from market.routers import router as market_router
from auth import auth_router
from database.connection import get_db, health_check, redis_health_check
from database.utils import get_database_stats, validate_database_integrity
from database.config import db_settings

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
app.include_router(auth_router, prefix="/api")


@app.get("/health")
async def health_check_endpoint():
    """Health check endpoint."""
    db_health = health_check()
    redis_health = redis_health_check()

    return {
        "status": "healthy" if db_health and redis_health else "unhealthy",
        "database": "healthy" if db_health else "unhealthy",
        "redis": "healthy" if redis_health else "unhealthy",
        "timestamp": "2024-01-15T10:30:00Z",
    }


@app.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with database statistics."""
    try:
        db_health = health_check()
        redis_health = redis_health_check()

        if not db_health:
            raise HTTPException(status_code=503, detail="Database connection failed")

        # Get database statistics
        stats = get_database_stats(db)
        integrity = validate_database_integrity(db)

        return {
            "status": "healthy" if db_health and redis_health else "unhealthy",
            "database": {
                "connection": "healthy" if db_health else "unhealthy",
                "redis": "healthy" if redis_health else "unhealthy",
                "statistics": stats,
                "integrity": integrity,
            },
            "timestamp": "2024-01-15T10:30:00Z",
        }

    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=db_settings.API_HOST,
        port=db_settings.API_PORT,
        log_level=db_settings.LOG_LEVEL.lower(),
    )
