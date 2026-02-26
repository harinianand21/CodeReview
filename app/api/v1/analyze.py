from fastapi import APIRouter, HTTPException, Depends
from app.models.analysis import AnalysisRequest, AnalysisResponse
from app.services.github_service import GitHubService
from app.analyzers import RepositoryAnalyzer

router = APIRouter()

def get_github_service() -> GitHubService:
    """
    Dependency provider for GitHubService.
    """
    return GitHubService()

def get_repository_analyzer() -> RepositoryAnalyzer:
    """
    Dependency provider for RepositoryAnalyzer.
    """
    return RepositoryAnalyzer()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_repository(
    request: AnalysisRequest,
    github_service: GitHubService = Depends(get_github_service),
    repo_analyzer: RepositoryAnalyzer = Depends(get_repository_analyzer)
) -> AnalysisResponse:
    """
    Analyzes a GitHub repository by its URL and returns metadata.
    
    - **repo_url**: The full URL of the GitHub repository.
    """
    try:
        metadata = github_service.get_repository_metadata(request.repo_url)
        structural_metrics = repo_analyzer.analyze(request.repo_url)
        
        return AnalysisResponse(
            name=metadata["repository_name"],
            stars=metadata["stars_count"],
            forks=metadata["forks_count"],
            language=metadata["primary_language"],
            commit_count=metadata["total_commit_count"],
            total_files=structural_metrics["total_files"],
            python_files=structural_metrics["python_files"],
            javascript_files=structural_metrics["javascript_files"],
            readme_exists=structural_metrics["readme_exists"],
            tests_exist=structural_metrics["tests_exist"]
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
