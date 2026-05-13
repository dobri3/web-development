from fastapi import FastAPI

from routers.auth_router import router as auth_router
from routers.movies_router import router as movies_router
from routers.recommendations_router import router as recommendations_router

app = FastAPI(title='fastapi_service', description='description', version='1.0.0')

app.include_router(auth_router)
app.include_router(recommendations_router)
app.include_router(movies_router)

@app.get('/health')
async def health():
    """Health endpoint"""
    return {"status": "ok"}