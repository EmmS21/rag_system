from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from api.models import Query
from rag.rag_workflow import rag_workflow 
from app.services.response_generator import ResponseGenerator
from uuid import uuid4

router = APIRouter()
queries_context = {}

@router.post("/query/")
async def receive_query(query: Query):
    query_id = str(uuid4())
    combined_texts = rag_workflow(query.query)
    queries_context[query_id] = {
        "combined_texts": combined_texts,
        "original_query": query.query
    }
    return {"query_id": query_id}

@router.get("/stream/{query_id}/", response_class=StreamingResponse)
async def stream_response(query_id: str):
    context = queries_context.get(query_id, None)
    if context is None or not context.get("combined_texts"):
        return StreamingResponse(iter(["No content available"]), media_type="text/event-stream")
    response_generator = ResponseGenerator()
    return StreamingResponse(response_generator.generate(context["combined_texts"], context["original_query"]), media_type="text/event-stream")
