from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers import auth_router, watchlist_router
from database import engine, Base
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up FastAPI service...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ready")
    
    yield
    
    logger.info("Shutting down...")
    await engine.dispose()
    logger.info("Shutdown complete")


app = FastAPI(
    title="Cinema FastAPI Service",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(auth_router.router)
app.include_router(watchlist_router.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "fastapi"}


@app.get("/ready")
async def ready():
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Ready check failed: {e}")
        return {"status": "not ready", "error": str(e)}