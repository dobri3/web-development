# main.py
from fastapi import FastAPI
from routers.auth_router import router as auth_router
from routers.watchlist_router import router as watchlist_router
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)

app = FastAPI(title="Cinema FastAPI Service")

app.include_router(auth_router)
app.include_router(watchlist_router)

@app.get("/health")
async def health():
    return {"status": "ok"}