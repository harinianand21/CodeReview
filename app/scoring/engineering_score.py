import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class EngineeringScorer:
    """
    Engine for calculating Engineering Maturity Scores for repositories.
    
    This class evaluates a repository based on code complexity, documentation,
    testing, and structural balance using proportional metrics to handle
    projects of various sizes fairly.
    """

    def __init__(self):
        # Weights for different categories (Total = 1.0)
        # Test presence weight slightly increased to 0.35
        self.weights = {
            "complexity_weight": 0.30,
            "structure_weight": 0.15,
            "documentation_weight": 0.10,
            "test_presence_weight": 0.35,
            "file_distribution_weight": 0.10
        }

    def _determine_grade(self, score: float) -> str:
        """Determines the letter grade (A/B/C/D) based on the total score."""
        if score >= 85: return "A"
        if score >= 70: return "B"
        if score >= 50: return "C"
        return "D"

    def calculate_complexity_score(
        self, 
        average_complexity: float, 
        max_complexity: int, 
        high_complexity_functions: int,
        python_files: int
    ) -> float:
        """
        Calculates a complexity health score (0-100).
        Uses proportional metrics (ratio) to avoid penalizing large projects unfairly.
        """
        # Scenario: No Python code analyzed
        if average_complexity == 0:
            return 50.0

        # 1. Base Score based on Average Complexity
        if 1.5 <= average_complexity <= 5.0:
            # Optimal Range: Balanced complexity
            base_score = 100.0
        elif average_complexity < 1.5:
            # Trivial Range: Very simple scripts
            base_score = 80.0
        elif 5.0 < average_complexity <= 10.0:
            # Moderate Density
            base_score = 100.0 - (average_complexity - 5.0) * 8
        else:
            # High Density (> 10)
            base_score = 60.0 - (average_complexity - 10.0) * 10

        # 2. Proportional High Complexity Penalty
        # Instead of raw count, we penalize based on the density of toxic functions
        if python_files > 0:
            high_comp_ratio = high_complexity_functions / python_files
            
            # Penalize only if more than 10% of files have high complexity
            if high_comp_ratio > 0.1:
                # Deduct points proportional to the excess ratio
                # E.g., a ratio of 0.3 (30%) would deduct (0.3 - 0.1) * 100 = 20 points
                ratio_deduction = (high_comp_ratio - 0.1) * 100
                base_score -= min(ratio_deduction, 30)
        
        # 3. Individual Extreme Outlier Deduction (Max CC)
        if max_complexity > 25:
            max_deduction = (max_complexity - 25) * 1.5
            base_score -= min(max_deduction, 20)
            
        return max(0.0, min(100.0, base_score))

    def calculate_documentation_score(self, readme_exists: bool) -> float:
        """Scores based on presence of essential documentation."""
        return 100.0 if readme_exists else 0.0

    def calculate_test_presence_score(self, tests_exist: bool) -> float:
        """Scores based on presence of a test suite."""
        return 100.0 if tests_exist else 0.0

    def calculate_structure_score(self, total_files: int) -> float:
        """Evaluates repository structure health."""
        if total_files == 0:
            return 0.0
        if total_files < 5:
            return 40.0
        return 100.0

    def calculate_distribution_score(
        self, 
        total_files: int, 
        python_files: int, 
        javascript_files: int
    ) -> float:
        """Scores based on the ratio of code files to total files."""
        if total_files == 0:
            return 0.0
        if python_files == 0:
            return 20.0
            
        code_files = python_files + javascript_files
        ratio = (code_files / total_files) * 100
        return min(ratio, 100.0)

    def calculate_score(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregates all metrics into a final engineering score and grade."""
        try:
            python_files = data.get("python_files", 0)
            
            complexity_score = self.calculate_complexity_score(
                data.get("average_complexity", 0.0),
                data.get("max_complexity", 0),
                data.get("high_complexity_functions", 0),
                python_files
            )
            
            doc_score = self.calculate_documentation_score(data.get("readme_exists", False))
            test_score = self.calculate_test_presence_score(data.get("tests_exist", False))
            struct_score = self.calculate_structure_score(data.get("total_files", 0))
            dist_score = self.calculate_distribution_score(
                data.get("total_files", 0),
                python_files,
                data.get("javascript_files", 0)
            )

            # Apply Weights (Sum = 1.0)
            total_score = (
                (complexity_score * self.weights["complexity_weight"]) +
                (struct_score * self.weights["structure_weight"]) +
                (doc_score * self.weights["documentation_weight"]) +
                (test_score * self.weights["test_presence_weight"]) +
                (dist_score * self.weights["file_distribution_weight"])
            )

            engineering_score = round(float(total_score), 2)
            
            return {
                "engineering_score": max(0.0, min(100.0, engineering_score)),
                "grade": self._determine_grade(engineering_score)
            }
            
        except Exception as e:
            logger.error(f"Error calculating engineering score: {e}")
            return {"engineering_score": 0.0, "grade": "D", "error": str(e)}

