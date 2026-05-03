from fastapi import FastAPI

app = FastAPI(title='fastapi_service', description='description', version='1.0.0')

@app.get('/health')
async def health():
    """Health endpoint"""
    return {"status": "ok"}