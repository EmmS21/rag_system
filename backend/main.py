from fastapi import APIRouter, FastAPI, Response
from fastapi.responses import StreamingResponse
import asyncio
from pydantic import BaseModel
from rag.rag_workflow import rag_workflow

app = FastAPI()
router = APIRouter()

class Query(BaseModel):
    query: str

# @app.get("/")
# def read_root():
#     return {"Hello": "World"}

@router.post("/query/", response_class=StreamingResponse)
async def generate_resp(query: Query):
    extracted_query = query.query
    response_generator = rag_workflow(extracted_query)
    return StreamingResponse(response_generator, media_type="text/plain")



app.include_router(router)
