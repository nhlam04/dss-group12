"""
Fund Allocation Optimizer
Allocates budget to grant requests based on TOPSIS rankings and constraints
"""

from typing import List, Tuple, Optional
import numpy as np
from charity_decision_system import (
    GrantRequest, AllocationDecision, FundAllocationResult
)
from topsis_analyzer import TOPSISAnalyzer


class FundAllocator:
    """
    Allocates funds to grant requests using various strategies
    """
    
    def __init__(self, total_budget: float, min_allocation_percentage: float = 0.5):
        """
        Initialize the fund allocator
        
        Args:
            total_budget: Total amount available for allocation
            min_allocation_percentage: Minimum % of request to fund (0-1)
                                      If we can't fund at least this much, reject
        """
        if total_budget <= 0:
            raise ValueError("Total budget must be positive")
        if not (0 <= min_allocation_percentage <= 1):
            raise ValueError("Min allocation percentage must be between 0 and 1")
        
        self.total_budget = total_budget
        self.min_allocation_percentage = min_allocation_percentage
        self.analyzer = TOPSISAnalyzer()
    
    def allocate_greedy(self, requests: List[GrantRequest], 
                       allow_partial: bool = True) -> FundAllocationResult:
        """
        Greedy allocation: Fund requests in priority order until budget exhausted
        
        Args:
            requests: List of grant requests to consider
            allow_partial: Whether to allow partial funding of requests
        
        Returns:
            FundAllocationResult with allocation decisions
        """
        # Rank requests using TOPSIS
        ranked_requests = self.analyzer.rank_requests(requests)
        
        remaining_budget = self.total_budget
        decisions = []
        
        for request, score, rank in ranked_requests:
            if remaining_budget <= 0:
                # No budget left, reject
                decision = AllocationDecision(
                    request=request,
                    amount_allocated=0,
                    allocation_percentage=0,
                    priority_score=score,
                    rank=rank,
                    rationale="Budget exhausted"
                )
                decisions.append(decision)
                continue
            
            # Determine allocation amount
            if remaining_budget >= request.amount_requested:
                # Can fully fund
                amount = request.amount_requested
                percentage = 1.0
                rationale = "Fully funded based on priority ranking"
            elif allow_partial and (remaining_budget / request.amount_requested) >= self.min_allocation_percentage:
                # Partial funding
                amount = remaining_budget
                percentage = amount / request.amount_requested
                rationale = f"Partially funded ({percentage:.0%}) - remaining budget constraint"
            else:
                # Cannot meet minimum threshold
                amount = 0
                percentage = 0
                rationale = f"Rejected - insufficient budget for minimum {self.min_allocation_percentage:.0%} funding"
            
            decision = AllocationDecision(
                request=request,
                amount_allocated=amount,
                allocation_percentage=percentage,
                priority_score=score,
                rank=rank,
                rationale=rationale
            )
            decisions.append(decision)
            remaining_budget -= amount
        
        return self._create_result(decisions)
    
    def allocate_proportional(self, requests: List[GrantRequest],
                             reserve_ratio: float = 0.1) -> FundAllocationResult:
        """
        Proportional allocation: Distribute budget proportional to TOPSIS scores
        
        Args:
            requests: List of grant requests
            reserve_ratio: Fraction of budget to keep in reserve (0-1)
        
        Returns:
            FundAllocationResult with allocation decisions
        """
        if not (0 <= reserve_ratio < 1):
            raise ValueError("Reserve ratio must be between 0 and 1")
        
        # Rank requests using TOPSIS
        ranked_requests = self.analyzer.rank_requests(requests)
        
        # Calculate allocatable budget
        allocatable_budget = self.total_budget * (1 - reserve_ratio)
        
        # Sum of all scores
        total_score = sum(score for _, score, _ in ranked_requests)
        
        if total_score == 0:
            # No valid requests, reject all
            decisions = [
                AllocationDecision(
                    request=request,
                    amount_allocated=0,
                    allocation_percentage=0,
                    priority_score=score,
                    rank=rank,
                    rationale="No valid scoring"
                )
                for request, score, rank in ranked_requests
            ]
            return self._create_result(decisions)
        
        decisions = []
        for request, score, rank in ranked_requests:
            # Allocate proportional to score
            proportional_allocation = (score / total_score) * allocatable_budget
            
            # Cap at requested amount
            amount = min(proportional_allocation, request.amount_requested)
            percentage = amount / request.amount_requested
            
            # Check minimum threshold
            if percentage < self.min_allocation_percentage:
                amount = 0
                percentage = 0
                rationale = f"Rejected - allocation below {self.min_allocation_percentage:.0%} threshold"
            else:
                if percentage >= 0.99:
                    rationale = f"Fully funded via proportional allocation"
                else:
                    rationale = f"Partially funded ({percentage:.0%}) via proportional allocation"
            
            decision = AllocationDecision(
                request=request,
                amount_allocated=amount,
                allocation_percentage=percentage,
                priority_score=score,
                rank=rank,
                rationale=rationale
            )
            decisions.append(decision)
        
        return self._create_result(decisions)
    
    def allocate_knapsack(self, requests: List[GrantRequest]) -> FundAllocationResult:
        """
        0/1 Knapsack allocation: Select combination that maximizes total impact
        Uses dynamic programming - only fully fund or reject (no partial)
        
        Maximizes: sum of (people_benefitted * success_rate * efficiency)
        """
        # Rank for ordering
        ranked_requests = self.analyzer.rank_requests(requests)
        
        n = len(requests)
        budget_int = int(self.total_budget)  # Convert to integer for DP
        
        # Value = risk-adjusted beneficiaries
        values = [
            int(req.people_benefitted * req.agent.success_rate * req.efficiency_ratio())
            for req, _, _ in ranked_requests
        ]
        weights = [int(req.amount_requested) for req, _, _ in ranked_requests]
        
        # DP table: dp[i][w] = max value using first i items with budget w
        dp = [[0] * (budget_int + 1) for _ in range(n + 1)]
        
        for i in range(1, n + 1):
            for w in range(budget_int + 1):
                # Don't take item i-1
                dp[i][w] = dp[i-1][w]
                
                # Take item i-1 if it fits
                if weights[i-1] <= w:
                    dp[i][w] = max(dp[i][w], dp[i-1][w-weights[i-1]] + values[i-1])
        
        # Backtrack to find which items were selected
        selected = [False] * n
        w = budget_int
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i-1][w]:
                selected[i-1] = True
                w -= weights[i-1]
        
        # Create decisions
        decisions = []
        for idx, (request, score, rank) in enumerate(ranked_requests):
            if selected[idx]:
                amount = request.amount_requested
                percentage = 1.0
                rationale = "Fully funded - optimal knapsack solution"
            else:
                amount = 0
                percentage = 0
                rationale = "Not selected in optimal solution"
            
            decision = AllocationDecision(
                request=request,
                amount_allocated=amount,
                allocation_percentage=percentage,
                priority_score=score,
                rank=rank,
                rationale=rationale
            )
            decisions.append(decision)
        
        return self._create_result(decisions)
    
    def _create_result(self, decisions: List[AllocationDecision]) -> FundAllocationResult:
        """Create a FundAllocationResult from decisions"""
        total_allocated = sum(d.amount_allocated for d in decisions)
        remaining = self.total_budget - total_allocated
        
        num_fully = sum(1 for d in decisions if d.is_fully_funded())
        num_partial = sum(1 for d in decisions if d.is_partially_funded())
        num_rejected = sum(1 for d in decisions if d.is_rejected())
        
        total_people = sum(
            int(d.request.risk_adjusted_benefit() * d.allocation_percentage)
            for d in decisions
        )
        
        # Calculate average efficiency of funded programs
        funded_decisions = [d for d in decisions if d.amount_allocated > 0]
        if funded_decisions:
            avg_efficiency = sum(
                d.request.efficiency_ratio() * d.amount_allocated
                for d in funded_decisions
            ) / total_allocated
        else:
            avg_efficiency = 0
        
        return FundAllocationResult(
            total_budget=self.total_budget,
            total_allocated=total_allocated,
            remaining_budget=remaining,
            decisions=decisions,
            num_fully_funded=num_fully,
            num_partially_funded=num_partial,
            num_rejected=num_rejected,
            total_people_benefitted=total_people,
            average_efficiency_ratio=avg_efficiency
        )
    
    def compare_strategies(self, requests: List[GrantRequest]) -> dict:
        """
        Compare different allocation strategies
        
        Returns:
            Dictionary with results from each strategy
        """
        return {
            'greedy_full': self.allocate_greedy(requests, allow_partial=False),
            'greedy_partial': self.allocate_greedy(requests, allow_partial=True),
            'proportional': self.allocate_proportional(requests),
            'knapsack': self.allocate_knapsack(requests)
        }
