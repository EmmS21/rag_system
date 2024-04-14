from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from api.models import Query
from rag.rag_workflow import rag_workflow 
from app.services.response_generator import ResponseGenerator

router = APIRouter()

@router.post("/query/", response_class=StreamingResponse)
async def generate_resp(query: Query):
    combined_texts = rag_workflow(query.query)
    try:
        response_generator = ResponseGenerator(model="gpt-3.5-turbo")
        response_stream = response_generator.generate(combined_texts, query.query)
        return StreamingResponse(response_stream, media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
