import logging
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Set

logger = logging.getLogger(__name__)

class RepositoryAnalyzer:
    """
    Service for cloning and analyzing GitHub repositories.
    
    This class handles the temporary local cloning of repositories, performs basic
    structural analysis, and ensures resources are cleaned up.
    
    Attributes:
        max_repo_size_mb (int): Maximum allowed size of the repository in MB.
        excluded_dirs (Set[str]): Set of directory names to exclude from file counts.
    """

    def __init__(self, max_repo_size_mb: int = 100):
        """
        Initializes the RepositoryAnalyzer with security constraints.
        
        Args:
            max_repo_size_mb (int): Limits the size of repos that can be analyzed.
        """
        self.max_repo_size_mb = max_repo_size_mb
        # Common directories to exclude from analysis to ensure accuracy and speed
        self.excluded_dirs = {".git", "node_modules", "venv", "__pycache__", "env", ".env", "dist", "build"}

    def _get_dir_size(self, path: Path) -> int:
        """
        Calculates the total size of a directory in bytes.
        
        Args:
            path (Path): The directory path to calculate size for.
            
        Returns:
            int: Size in bytes.
        """
        total_size = 0
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    total_size += item.stat().st_size
        except OSError as e:
            logger.error(f"Error calculating directory size: {e}")
        return total_size

    def analyze(self, repo_url: str, complexity_analyzer: Any = None) -> Dict[str, Any]:
        """
        Clones a repository, analyzes its structure, and returns metrics.
        
        The analysis includes counting files and detecting the presence of 
        standard project files like README and test directories.
        
        Args:
            repo_url (str): The HTTPS URL of the GitHub repository.
            complexity_analyzer (Any): Optional instance of ComplexityAnalyzer.
            
        Returns:
            Dict[str, Any]: A dictionary containing structural and complexity metrics.
        """
        results = {
            "total_files": 0,
            "python_files": 0,
            "javascript_files": 0,
            "readme_exists": False,
            "tests_exist": False,
            "average_complexity": 0.0,
            "max_complexity": 0,
            "high_complexity_functions": 0
        }

        # TemporaryDirectory ensures cleanup even if exceptions occur
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                # Clone the repository
                subprocess.run(
                    ["git", "clone", "--depth", "1", repo_url, "."],
                    cwd=temp_dir,
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                # Enforce security constraint
                repo_size_bytes = self._get_dir_size(temp_path)
                if repo_size_bytes > self.max_repo_size_mb * 1024 * 1024:
                    raise ValueError(
                        f"Repository size ({repo_size_bytes / (1024*1024):.2f} MB) "
                        f"exceeds the limit of {self.max_repo_size_mb} MB."
                    )
                
                # Structural analysis
                self._run_structural_analysis(temp_path, results)

                # Complexity analysis (if provided)
                if complexity_analyzer:
                    comp_results = complexity_analyzer.analyze(str(temp_path))
                    results.update(comp_results)
                
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr.strip().split('\n')[-1] if e.stderr else "Unknown git error"
                logger.error(f"Clone failed: {error_msg}")
                raise ValueError(f"Failed to clone repository: {error_msg}")
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                raise

        return results

    def _run_structural_analysis(self, repo_path: Path, results: Dict[str, Any]) -> None:
        """
        Internal method to walk the repository and gather file metrics.
        
        Args:
            repo_path (Path): Local path to the cloned repository.
            results (Dict[str, Any]): Dictionary to populate with results.
        """
        # Detect README file (case-insensitive check for common variations)
        readme_variations = ["README.md", "README", "readme.md", "README.txt"]
        results["readme_exists"] = any((repo_path / name).exists() for name in readme_variations)

        # Detect tests directory (root level common names)
        test_dirs = ["tests", "test", "spec", "testing"]
        results["tests_exist"] = any(
            (repo_path / name).is_dir() for name in test_dirs
        )

        # Walk through files and categorize
        for item in repo_path.rglob('*'):
            # Skip items inside excluded directories
            if any(part in self.excluded_dirs for part in item.relative_to(repo_path).parts):
                continue
                
            if item.is_file():
                results["total_files"] += 1
                
                # Check file extensions
                suffix = item.suffix.lower()
                if suffix == ".py":
                    results["python_files"] += 1
                elif suffix == ".js":
                    results["javascript_files"] += 1
