from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str
    k: Optional[int] = 5

class LegalDocument(BaseModel):
    id: str
    title: str
    text: str
    article_number: int
    page: int
    source: str
    law_name: str
    word_count: int
    char_count: int

class QueryResponse(BaseModel):
    query: str
    results: List[LegalDocument]
    total_results: int
    processing_time: float

class HealthResponse(BaseModel):
    status: str
    message: str
    version: str
