# main.py
from fastapi import FastAPI
from routers.auth_router import router as auth_router
from routers.watchlist_router import router as watchlist_router
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
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
    return {
        "success": True,
        "data": {
            "status": "ok"
        }
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": "HTTP_ERROR",
                "detail": exc.detail,
                "status_code": exc.status_code,
            },
        },
    )