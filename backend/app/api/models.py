from pydantic import BaseModel
from typing import Optional

class Query(BaseModel):
    query: str

class ExtendedQuery(Query):
    context: Optional[str] = None
