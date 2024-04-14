from fastapi import FastAPI
from api.router import router as api_router

app = FastAPI(title="Colombia Real Estate Legal ChatBot API", version="1.0")
app.include_router(api_router)
