from fastapi import FastAPI
from routers.auth_router import router as auth_router
import logging

app = FastAPI(title='fastapi_service', description='description', version='1.0.0')

logging.basicConfig(level=logging.INFO)

app.include_router(auth_router)

@app.get('/health')
async def health():
    """Health endpoint"""
    return {"status": "ok"}



