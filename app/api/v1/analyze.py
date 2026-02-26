from fastapi import APIRouter, HTTPException, Depends
from app.models.analysis import AnalysisRequest, AnalysisResponse
from app.services.github_service import GitHubService

router = APIRouter()

def get_github_service() -> GitHubService:
    """
    Dependency provider for GitHubService.
    """
    return GitHubService()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_repository(
    request: AnalysisRequest,
    github_service: GitHubService = Depends(get_github_service)
) -> AnalysisResponse:
    """
    Analyzes a GitHub repository by its URL and returns metadata.
    
    - **repo_url**: The full URL of the GitHub repository.
    """
    try:
        metadata = github_service.get_repository_metadata(request.repo_url)
        
        return AnalysisResponse(
            name=metadata["repository_name"],
            stars=metadata["stars_count"],
            forks=metadata["forks_count"],
            language=metadata["primary_language"],
            commit_count=metadata["total_commit_count"]
        )
        
    except ValueError as e:
        # Handle invalid URL or repository not found
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        # Handle GitHub API errors (unauthorized, rate limit, etc.)
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        # Handle unexpected internal errors
        raise HTTPException(status_code=500, detail="An unexpected error occurred during analysis.")
