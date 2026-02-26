from fastapi import APIRouter, HTTPException, Depends
from app.models.analysis import AnalysisRequest, AnalysisResponse
from app.services.github_service import GitHubService
from app.analyzers import RepositoryAnalyzer, ComplexityAnalyzer

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

def get_complexity_analyzer() -> ComplexityAnalyzer:
    """
    Dependency provider for ComplexityAnalyzer.
    """
    return ComplexityAnalyzer()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_repository(
    request: AnalysisRequest,
    github_service: GitHubService = Depends(get_github_service),
    repo_analyzer: RepositoryAnalyzer = Depends(get_repository_analyzer),
    complexity_analyzer: ComplexityAnalyzer = Depends(get_complexity_analyzer)
) -> AnalysisResponse:
    """
    Analyzes a GitHub repository by its URL and returns metadata.
    
    - **repo_url**: The full URL of the GitHub repository.
    """
    try:
        metadata = github_service.get_repository_metadata(request.repo_url)
        analysis_results = repo_analyzer.analyze(
            request.repo_url, 
            complexity_analyzer=complexity_analyzer
        )
        
        return AnalysisResponse(
            name=metadata["repository_name"],
            stars=metadata["stars_count"],
            forks=metadata["forks_count"],
            language=metadata["primary_language"],
            commit_count=metadata["total_commit_count"],
            total_files=analysis_results["total_files"],
            python_files=analysis_results["python_files"],
            javascript_files=analysis_results["javascript_files"],
            readme_exists=analysis_results["readme_exists"],
            tests_exist=analysis_results["tests_exist"],
            average_complexity=analysis_results["average_complexity"],
            max_complexity=analysis_results["max_complexity"],
            high_complexity_functions=analysis_results["high_complexity_functions"]
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
