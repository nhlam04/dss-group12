
from typing import List, Tuple, Optional
import numpy as np
from charity_decision_system import (
    GrantRequest, AllocationDecision, FundAllocationResult
)
from topsis_analyzer import TOPSISAnalyzer


class FundAllocator:
    
    def __init__(self, total_budget: float, min_allocation_percentage: float = 0.5):
        if total_budget <= 0:
            raise ValueError("Quỹ phải là số dương")
        if not (0 <= min_allocation_percentage <= 1):
            raise ValueError("Tỷ lệ phân bổ tối thểu phải là giá trị giữa 0 và 1")
        
        self.total_budget = total_budget
        self.min_allocation_percentage = min_allocation_percentage
        self.analyzer = TOPSISAnalyzer()
    
    def allocate_greedy(self, requests: List[GrantRequest], 
                       allow_partial: bool = True) -> FundAllocationResult:

        ranked_requests = self.analyzer.rank_requests(requests)
        
        remaining_budget = self.total_budget
        decisions = []
        
        for request, score, rank in ranked_requests:
            if remaining_budget <= 0:
                decision = AllocationDecision(
                    request=request,
                    amount_allocated=0,
                    allocation_percentage=0,
                    priority_score=score,
                    rank=rank,
                    rationale="Hết quỹ"
                )
                decisions.append(decision)
                continue

            if remaining_budget >= request.amount_requested:
                amount = request.amount_requested
                percentage = 1.0
                rationale = "Từ thiện hoàn toàn dựa theo mức độ cấp bách"
            elif allow_partial and (remaining_budget / request.amount_requested) >= self.min_allocation_percentage:
                amount = remaining_budget
                percentage = amount / request.amount_requested
                rationale = f"Từ thiện ({percentage:.0%}) - ràng buộc ngân sách còn lại"
            else:
                amount = 0
                percentage = 0
                rationale = f"Từ chối - Không đ ngân sách để từ thiện {self.min_allocation_percentage:.0%}"
            
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

        if not (0 <= reserve_ratio < 1):
            raise ValueError("Tỷ lệ dự phòng phải nằm trong khoảng từ 0 đến 1.")

        ranked_requests = self.analyzer.rank_requests(requests)

        allocatable_budget = self.total_budget * (1 - reserve_ratio)

        total_score = sum(score for _, score, _ in ranked_requests)
        
        if total_score == 0:
            decisions = [
                AllocationDecision(
                    request=request,
                    amount_allocated=0,
                    allocation_percentage=0,
                    priority_score=score,
                    rank=rank,
                    rationale="Không c mức độ đánh giá hợp lý"
                )
                for request, score, rank in ranked_requests
            ]
            return self._create_result(decisions)
        
        decisions = []
        for request, score, rank in ranked_requests:
            proportional_allocation = (score / total_score) * allocatable_budget

            amount = min(proportional_allocation, request.amount_requested)
            percentage = amount / request.amount_requested

            if percentage < self.min_allocation_percentage:
                amount = 0
                percentage = 0
                rationale = f"Từ chối - phân bổ dưới  {self.min_allocation_percentage:.0%}"
            else:
                if percentage >= 0.99:
                    rationale = f"Từ thiện toàn phần dựa theo xếp hạng phân bổ"
                else:
                    rationale = f"Từ thiện ({percentage:.0%}) dựa theo phân bổ một phần"
            
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

        ranked_requests = self.analyzer.rank_requests(requests)
        
        n = len(requests)
        budget_int = int(self.total_budget)

        values = [
            int(req.people_benefitted * req.agent.success_rate * req.efficiency_ratio())
            for req, _, _ in ranked_requests
        ]
        weights = [int(req.amount_requested) for req, _, _ in ranked_requests]

        dp = [[0] * (budget_int + 1) for _ in range(n + 1)]
        
        for i in range(1, n + 1):
            for w in range(budget_int + 1):
                dp[i][w] = dp[i-1][w]

                if weights[i-1] <= w:
                    dp[i][w] = max(dp[i][w], dp[i-1][w-weights[i-1]] + values[i-1])

        selected = [False] * n
        w = budget_int
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i-1][w]:
                selected[i-1] = True
                w -= weights[i-1]

        decisions = []
        for idx, (request, score, rank) in enumerate(ranked_requests):
            if selected[idx]:
                amount = request.amount_requested
                percentage = 1.0
                rationale = "Từ thiện hoàn toàn - optimal knapsack solution"
            else:
                amount = 0
                percentage = 0
                rationale = "Không có giải pháp nào được chọn"
            
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
        total_allocated = sum(d.amount_allocated for d in decisions)
        remaining = self.total_budget - total_allocated
        
        num_fully = sum(1 for d in decisions if d.is_fully_funded())
        num_partial = sum(1 for d in decisions if d.is_partially_funded())
        num_rejected = sum(1 for d in decisions if d.is_rejected())
        
        total_people = sum(
            int(d.request.risk_adjusted_benefit() * d.allocation_percentage)
            for d in decisions
        )

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
        return {
            'greedy_hoàn toàn': self.allocate_greedy(requests, allow_partial=False),
            'greedy_một phần': self.allocate_greedy(requests, allow_partial=True),
            'theo tỷ lệ': self.allocate_proportional(requests),
            'knapsack': self.allocate_knapsack(requests)
        }
