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
    total_files: int
    python_files: int
    javascript_files: int
    readme_exists: bool
    tests_exist: bool
