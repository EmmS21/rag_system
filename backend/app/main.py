import os
os.environ['TOKENIZERS_PARALLELISM'] = 'false'


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.router import router as api_router

app = FastAPI(title="Colombia Real Estate Legal ChatBot API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  
        "https://propabroad.vercel.app"  
    ],  
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],  
)

app.include_router(api_router)
