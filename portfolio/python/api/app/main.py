from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio
from contextlib import asynccontextmanager

from app.config import settings
from app.core.database.connection import init_db, create_tables, get_db_health
from app.core.database.init_db import init_database
from app.health_check import router as health_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - runs on startup and shutdown."""
    # Startup
    logger.info("Starting Portfolia API...")
    
    try:
        # Initialize database connection
        logger.info("Initializing database connection...")
        await init_db()
        
        # Run database migrations and create schemas
        logger.info("Running database migrations and creating schemas...")
        await create_tables()
        
        # Initialize database with sample data if needed
        logger.info("Initializing database with sample data...")
        await init_database()
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # Don't fail startup - allow app to run with degraded functionality
        logger.warning("Application starting with degraded database functionality")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Portfolia API...")


# Create FastAPI app with lifespan management
app = FastAPI(
    title="Portfolia API",
    description="Portfolio management and trading strategy API",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/health", tags=["health"])

# Include API v1 routers
try:
    from api.v1.test_router import router as test_router
    app.include_router(test_router, prefix="/api/v1", tags=["test"])
    logger.info("Test router included successfully")
except ImportError as e:
    logger.warning(f"Could not import test router: {e}")

# Include authentication router
try:
    from app.core.auth.router import router as auth_router
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
    logger.info("Auth router included successfully")
except ImportError as e:
    logger.warning(f"Could not import auth router: {e}")

# Include market router
try:
    from api.v1.market.routers import router as market_router
    app.include_router(market_router, prefix="/api/v1", tags=["market-data"])
    logger.info("Market router included successfully")
except ImportError as e:
    logger.warning(f"Could not import market router: {e}")

# Include statistical indicators router
try:
    from utils.indicators.routers import router as indicators_router
    app.include_router(indicators_router, prefix="/api/v1", tags=["statistical-indicators"])
    logger.info("Statistical indicators router included successfully")
except ImportError as e:
    logger.warning(f"Could not import statistical indicators router: {e}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Portfolia API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/api/v1/")
async def api_root():
    """API root endpoint."""
    return {
        "message": "Portfolia API v1",
        "endpoints": {
            "health": "/health",
            "test": "/api/v1/test",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
