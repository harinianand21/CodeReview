import logging
from pathlib import Path
from typing import Dict, Any, List
from radon.visitors import ComplexityVisitor
from radon.complexity import cc_visit

logger = logging.getLogger(__name__)

class ComplexityAnalyzer:
    """
    Service for analyzing cyclomatic complexity in Python files.
    
    Uses the radon library to compute metrics for functions and classes.
    """

    def __init__(self, high_complexity_threshold: int = 10):
        """
        Initializes the ComplexityAnalyzer.
        
        Args:
            high_complexity_threshold (int): The complexity score above which a function
                                             is considered "high complexity".
        """
        self.threshold = high_complexity_threshold

    def analyze(self, repo_path: str) -> Dict[str, Any]:
        """
        Walks through the repository and calculates complexity metrics for all Python files.
        
        Args:
            repo_path (str): The local filesystem path to the repository.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - average_complexity (float): Mean complexity across all measured blocks.
                - max_complexity (int): Highest complexity score found.
                - high_complexity_functions (int): Count of functions exceeding the threshold.
        """
        path = Path(repo_path)
        all_complexities: List[int] = []
        high_complexity_count = 0
        max_comp = 0

        try:
            for py_file in path.rglob("*.py"):
                # Skip common noise patterns if encountered in the walk
                if any(part in {".venv", "venv", "node_modules", "__pycache__"} for part in py_file.parts):
                    continue

                try:
                    file_content = py_file.read_text(encoding="utf-8")
                    # cc_visit returns a list of Function or Class blocks with complexity info
                    blocks = cc_visit(file_content)
                    
                    for block in blocks:
                        complexity = block.complexity
                        all_complexities.append(complexity)
                        
                        if complexity > max_comp:
                            max_comp = complexity
                            
                        if complexity > self.threshold:
                            high_complexity_count += 1
                            
                except Exception as e:
                    logger.warning(f"Could not analyze complexity for {py_file}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error during complexity analysis of {repo_path}: {e}")
            # Ensure we return a valid structure even on failure
            return {
                "average_complexity": 0.0,
                "max_complexity": 0,
                "high_complexity_functions": 0
            }

        avg_complexity = sum(all_complexities) / len(all_complexities) if all_complexities else 0.0

        return {
            "average_complexity": round(avg_complexity, 2),
            "max_complexity": max_comp,
            "high_complexity_functions": high_complexity_count
        }
