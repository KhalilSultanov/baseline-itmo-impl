from typing import List
from pydantic import BaseModel, HttpUrl, constr


class PredictionRequest(BaseModel):
    id: int
    query: constr(min_length=1, strip_whitespace=True)


class PredictionResponse(BaseModel):
    id: int
    answer: int | None = None
    reasoning: str
    sources: List[HttpUrl]
