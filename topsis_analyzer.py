"""
TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)
Multi-criteria decision analysis for ranking grant requests
"""

import numpy as np
from typing import List, Dict, Tuple
from charity_decision_system import GrantRequest, UrgencyLevel


class TOPSISAnalyzer:
    """
    Implements TOPSIS algorithm for multi-criteria decision making
    """
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize TOPSIS analyzer with criteria weights
        
        Args:
            weights: Dictionary of criterion name to weight (must sum to 1)
        """
        # Default weights for criteria
        self.default_weights = {
            'people_benefitted': 0.25,      # Impact scale
            'efficiency': 0.20,              # Low overhead
            'success_rate': 0.15,            # Track record
            'cost_effectiveness': 0.15,      # Cost per person
            'urgency': 0.10,                 # Time sensitivity
            'sustainability': 0.10,          # Long-term value
            'transparency': 0.05,            # Accountability
        }
        
        self.weights = weights if weights else self.default_weights
        self._validate_weights()
    
    def _validate_weights(self):
        """Ensure weights sum to approximately 1"""
        total = sum(self.weights.values())
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"Weights must sum to 1, got {total}")
    
    def extract_criteria_matrix(self, requests: List[GrantRequest]) -> Tuple[np.ndarray, List[str]]:
        """
        Extract criteria values from grant requests into a decision matrix
        
        Returns:
            Tuple of (decision_matrix, criterion_names)
        """
        criteria = []
        criterion_names = [
            'people_benefitted',
            'efficiency',
            'success_rate',
            'cost_effectiveness',
            'urgency',
            'sustainability',
            'transparency'
        ]
        
        for request in requests:
            # Higher is better for all criteria
            criteria.append([
                request.people_benefitted,                    # More people = better
                request.efficiency_ratio(),                   # Lower overhead = better
                request.agent.success_rate,                   # Higher success = better
                1 / request.net_cost_per_person(),           # Lower cost/person = better (inverted)
                request.urgency.value,                        # Higher urgency = better
                request.sustainability_score,                 # Higher sustainability = better
                request.agent.transparency_score,             # Higher transparency = better
            ])
        
        return np.array(criteria), criterion_names
    
    def normalize_matrix(self, matrix: np.ndarray) -> np.ndarray:
        """
        Normalize the decision matrix using vector normalization
        
        Each element is divided by the square root of sum of squares in its column
        """
        # Calculate the sum of squares for each column
        sum_of_squares = np.sqrt(np.sum(matrix ** 2, axis=0))
        
        # Avoid division by zero
        sum_of_squares[sum_of_squares == 0] = 1
        
        # Normalize
        normalized = matrix / sum_of_squares
        return normalized
    
    def apply_weights(self, normalized_matrix: np.ndarray, criterion_names: List[str]) -> np.ndarray:
        """
        Apply weights to normalized matrix
        """
        weights_array = np.array([self.weights[name] for name in criterion_names])
        return normalized_matrix * weights_array
    
    def calculate_ideal_solutions(self, weighted_matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate ideal best and worst solutions
        
        For benefit criteria (all our criteria), ideal best is maximum
        """
        ideal_best = np.max(weighted_matrix, axis=0)
        ideal_worst = np.min(weighted_matrix, axis=0)
        
        return ideal_best, ideal_worst
    
    def calculate_distances(self, weighted_matrix: np.ndarray, 
                           ideal_best: np.ndarray, 
                           ideal_worst: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate Euclidean distances to ideal best and worst solutions
        """
        # Distance to ideal best
        dist_to_best = np.sqrt(np.sum((weighted_matrix - ideal_best) ** 2, axis=1))
        
        # Distance to ideal worst
        dist_to_worst = np.sqrt(np.sum((weighted_matrix - ideal_worst) ** 2, axis=1))
        
        return dist_to_best, dist_to_worst
    
    def calculate_scores(self, dist_to_best: np.ndarray, dist_to_worst: np.ndarray) -> np.ndarray:
        """
        Calculate TOPSIS scores (closeness to ideal solution)
        
        Score = distance_to_worst / (distance_to_best + distance_to_worst)
        Higher score is better
        """
        # Avoid division by zero
        total_distance = dist_to_best + dist_to_worst
        total_distance[total_distance == 0] = 1e-10
        
        scores = dist_to_worst / total_distance
        return scores
    
    def rank_requests(self, requests: List[GrantRequest]) -> List[Tuple[GrantRequest, float, int]]:
        """
        Rank grant requests using TOPSIS
        
        Returns:
            List of tuples (request, score, rank) sorted by rank
        """
        if not requests:
            return []
        
        # Step 1: Extract criteria matrix
        matrix, criterion_names = self.extract_criteria_matrix(requests)
        
        # Step 2: Normalize the matrix
        normalized = self.normalize_matrix(matrix)
        
        # Step 3: Apply weights
        weighted = self.apply_weights(normalized, criterion_names)
        
        # Step 4: Calculate ideal solutions
        ideal_best, ideal_worst = self.calculate_ideal_solutions(weighted)
        
        # Step 5: Calculate distances
        dist_to_best, dist_to_worst = self.calculate_distances(weighted, ideal_best, ideal_worst)
        
        # Step 6: Calculate scores
        scores = self.calculate_scores(dist_to_best, dist_to_worst)
        
        # Step 7: Rank (sort by score descending)
        ranked_indices = np.argsort(scores)[::-1]
        
        # Create result list with rankings
        results = []
        for rank, idx in enumerate(ranked_indices, start=1):
            results.append((requests[idx], scores[idx], rank))
        
        return results
    
    def explain_ranking(self, request: GrantRequest, score: float) -> str:
        """
        Generate an explanation for a request's ranking
        """
        explanation = f"Priority Score: {score:.3f}\n"
        explanation += f"- Benefits {request.people_benefitted:,} people\n"
        explanation += f"- Efficiency: {request.efficiency_ratio():.1%} (${request.net_cost_per_person():.2f}/person)\n"
        explanation += f"- Agent success rate: {request.agent.success_rate:.1%}\n"
        explanation += f"- Urgency: {request.urgency.name}\n"
        explanation += f"- Sustainability: {request.sustainability_score:.1%}\n"
        
        return explanation
