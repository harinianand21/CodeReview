from typing import Optional
from pydantic import BaseModel, HttpUrl

class AnalysisRequest(BaseModel):
    """
    Schema for repository analysis request.
    """
    repo_url: str

class AnalysisResponse(BaseModel):
    """
    Schema for repository analysis response.
    """
    name: str
    stars: int
    forks: int
    language: Optional[str]
    commit_count: int
