import re
from typing import Dict, Any, Optional
from github import Github, GithubException, Auth
from app.core.config import settings

class GitHubService:
    """
    Service to interact with GitHub API using PyGithub to fetch repository metadata.
    """

    def __init__(self, token: Optional[str] = None):
        """
        Initialize the GitHub service with an optional token.
        If no token is provided, it attempts to use GITHUB_TOKEN from settings.
        """
        self.token = token or settings.GITHUB_TOKEN
        auth = Auth.Token(self.token) if self.token else None
        self.gh = Github(auth=auth)

    def _extract_repo_info(self, url: str) -> Dict[str, str]:
        """
        Extracts owner and repository name from a GitHub URL.
        
        Args:
            url: The GitHub repository URL.
            
        Returns:
            A dictionary containing 'owner' and 'repo'.
            
        Raises:
            ValueError: If the URL is invalid or doesn't match Github format.
        """
        # Clean URL (remove trailing slashes and .git)
        cleaned_url = url.rstrip("/").replace(".git", "")
        
        # Regex to handle https://github.com/owner/repo or github.com/owner/repo
        pattern = r"(?:https?://)?(?:www\.)?github\.com/([^/]+)/([^/]+)"
        match = re.search(pattern, cleaned_url)
        
        if not match:
            raise ValueError(f"Invalid GitHub repository URL: {url}")
            
        return {
            "owner": match.group(1),
            "repo_name": match.group(2)
        }

    def get_repository_metadata(self, url: str) -> Dict[str, Any]:
        """
        Fetches metadata for a given GitHub repository URL.
        
        Args:
            url: The GitHub repository URL.
            
        Returns:
            Dict containing name, stars, forks, language, and commit count.
            
        Raises:
            ValueError: If repository is not found or URL is invalid.
            RuntimeError: For general GitHub API errors.
        """
        info = self._extract_repo_info(url)
        owner_repo = f"{info['owner']}/{info['repo_name']}"

        try:
            repo = self.gh.get_repo(owner_repo)
            
            # Fetch total commit count safely
            # Note: totalCount uses the GitHub API's 'Link' header for pagination counting
            try:
                commit_count = repo.get_commits().totalCount
            except GithubException:
                commit_count = 0  # Fallback if commits are inaccessible

            return {
                "repository_name": repo.name,
                "stars_count": repo.stargazers_count,
                "forks_count": repo.forks_count,
                "primary_language": repo.language,
                "total_commit_count": commit_count,
                "owner": repo.owner.login,
                "description": repo.description
            }

        except GithubException as e:
            if e.status == 404:
                raise ValueError(f"Repository not found: {owner_repo}")
            elif e.status == 401:
                raise RuntimeError("Unauthorized: Please check your GITHUB_TOKEN")
            elif e.status == 403:
                raise RuntimeError("Rate limit exceeded or forbidden access to repository")
            else:
                raise RuntimeError(f"GitHub API error: {e.data.get('message', str(e))}")
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred: {str(e)}")
