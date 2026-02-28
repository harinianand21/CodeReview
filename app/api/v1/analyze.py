from fastapi import APIRouter, HTTPException, Depends
from app.models.analysis import AnalysisRequest, AnalysisResponse
from app.services.github_service import GitHubService
from app.analyzers import RepositoryAnalyzer, ComplexityAnalyzer
from app.scoring.engineering_score import EngineeringScorer

router = APIRouter()

def get_github_service() -> GitHubService:
    """Dependency provider for GitHubService."""
    return GitHubService()

def get_repository_analyzer() -> RepositoryAnalyzer:
    """Dependency provider for RepositoryAnalyzer."""
    return RepositoryAnalyzer()

def get_complexity_analyzer() -> ComplexityAnalyzer:
    """Dependency provider for ComplexityAnalyzer."""
    return ComplexityAnalyzer()

def get_engineering_scorer() -> EngineeringScorer:
    """Dependency provider for EngineeringScorer."""
    return EngineeringScorer()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_repository(
    request: AnalysisRequest,
    github_service: GitHubService = Depends(get_github_service),
    repo_analyzer: RepositoryAnalyzer = Depends(get_repository_analyzer),
    complexity_analyzer: ComplexityAnalyzer = Depends(get_complexity_analyzer),
    engineering_scorer: EngineeringScorer = Depends(get_engineering_scorer)
) -> AnalysisResponse:
    """
    Analyzes a GitHub repository and returns comprehensive technical metrics including a maturity score.
    """
    try:
        # 1. Fetch data from GitHub API
        metadata = github_service.get_repository_metadata(request.repo_url)
        
        # 2. Perform deep analysis (cloning + complexity calculation)
        analysis_results = repo_analyzer.analyze(
            request.repo_url, 
            complexity_analyzer=complexity_analyzer
        )
        
        # 3. Calculate Engineering Maturity Score
        scoring_results = engineering_scorer.calculate_score(analysis_results)
        
        # 4. Map everything to the final response schema
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
            high_complexity_functions=analysis_results["high_complexity_functions"],
            engineering_score=scoring_results["engineering_score"],
            grade=scoring_results["grade"]
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
