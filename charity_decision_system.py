"""
Charity Fund Decision Support System

A multi-criteria decision-making system that helps charity funds allocate
resources to grant requests using TOPSIS ranking and optimization algorithms.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum
import numpy as np
from datetime import datetime


class ProgramCategory(Enum):
    """Categories of charity programs"""
    HEALTHCARE = "Healthcare"
    EDUCATION = "Education"
    FOOD_SECURITY = "Food Security"
    DISASTER_RELIEF = "Disaster Relief"
    HOUSING = "Housing"
    ENVIRONMENT = "Environment"
    OTHER = "Other"


class UrgencyLevel(Enum):
    """Urgency levels for programs"""
    CRITICAL = 5  # Immediate need (e.g., disaster relief)
    HIGH = 4      # Urgent but not immediate
    MEDIUM = 3    # Standard timeline
    LOW = 2       # Can be delayed
    FLEXIBLE = 1  # No time constraints


@dataclass
class CharityAgent:
    """Represents an organization requesting funds"""
    agent_id: str
    name: str
    transparency_score: float  # Accountability score (0-1)
    total_programs_completed: int
    programs_succeeded: int
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate from completed programs"""
        if self.total_programs_completed == 0:
            return 0.0
        return self.programs_succeeded / self.total_programs_completed
    
    def __post_init__(self):
        if self.total_programs_completed < 0:
            raise ValueError("Total programs completed must be non-negative")
        if self.programs_succeeded < 0:
            raise ValueError("Programs succeeded must be non-negative")
        if self.programs_succeeded > self.total_programs_completed:
            raise ValueError("Programs succeeded cannot exceed total programs")
        if not (0 <= self.transparency_score <= 1):
            raise ValueError("Transparency score must be between 0 and 1")


@dataclass
class GrantRequest:
    """Represents a grant request for a charity program"""
    request_id: str
    agent: CharityAgent
    program_name: str
    amount_requested: float  # Total amount in dollars
    overhead_cost: float     # Non-charity administrative costs
    people_benefitted: int   # Number of people impacted
    duration_months: int     # Time to complete program
    category: ProgramCategory
    urgency: UrgencyLevel
    sustainability_score: float  # Long-term impact score (0-1)
    status: str = 'pending'  # 'pending', 'funded', 'rejected', or 'completed'
    succeeded: Optional[bool] = None  # Only relevant if status is 'funded' or 'rejected'
    
    # Calculated fields
    net_charity_amount: float = field(init=False)
    overhead_ratio: float = field(init=False)
    
    def __post_init__(self):
        if self.amount_requested <= 0:
            raise ValueError("Amount requested must be positive")
        if self.overhead_cost < 0:
            raise ValueError("Overhead cost cannot be negative")
        if self.overhead_cost >= self.amount_requested:
            raise ValueError("Overhead cost cannot exceed total amount")
        if self.people_benefitted <= 0:
            raise ValueError("People benefitted must be positive")
        if self.duration_months <= 0:
            raise ValueError("Duration must be positive")
        if not (0 <= self.sustainability_score <= 1):
            raise ValueError("Sustainability score must be between 0 and 1")
        if self.status not in ['pending', 'funded', 'rejected', 'completed']:
            raise ValueError("Status must be 'pending', 'funded', 'rejected', or 'completed'")
        
        self.net_charity_amount = self.amount_requested - self.overhead_cost
        self.overhead_ratio = self.overhead_cost / self.amount_requested
    
    def cost_per_person(self) -> float:
        """Calculate cost per person benefitted"""
        return self.amount_requested / self.people_benefitted
    
    def net_cost_per_person(self) -> float:
        """Calculate net cost per person (excluding overhead)"""
        return self.net_charity_amount / self.people_benefitted
    
    def monthly_impact(self) -> float:
        """Calculate people benefitted per month"""
        return self.people_benefitted / self.duration_months
    
    def efficiency_ratio(self) -> float:
        """Calculate ratio of money going to charity vs overhead"""
        return 1 - self.overhead_ratio
    
    def risk_adjusted_benefit(self) -> float:
        """Calculate expected benefit adjusted for agent's success rate"""
        return self.people_benefitted * self.agent.success_rate


@dataclass
class AllocationDecision:
    """Represents a funding allocation decision"""
    request: GrantRequest
    amount_allocated: float
    allocation_percentage: float  # What % of request was granted
    priority_score: float  # TOPSIS score
    rank: int  # Ranking among all requests
    rationale: str  # Explanation of decision
    
    def is_fully_funded(self) -> bool:
        return self.allocation_percentage >= 0.99  # 99% or more
    
    def is_partially_funded(self) -> bool:
        return 0 < self.allocation_percentage < 0.99
    
    def is_rejected(self) -> bool:
        return self.allocation_percentage == 0


@dataclass
class FundAllocationResult:
    """Results of the fund allocation process"""
    total_budget: float
    total_allocated: float
    remaining_budget: float
    decisions: List[AllocationDecision]
    num_fully_funded: int
    num_partially_funded: int
    num_rejected: int
    total_people_benefitted: int
    average_efficiency_ratio: float
    
    def utilization_rate(self) -> float:
        """Calculate budget utilization percentage"""
        return (self.total_allocated / self.total_budget) * 100
    
    def summary(self) -> str:
        """Generate a summary report"""
        return f"""
Fund Allocation Summary:
------------------------
Total Budget: ${self.total_budget:,.2f}
Total Allocated: ${self.total_allocated:,.2f}
Remaining: ${self.remaining_budget:,.2f}
Utilization Rate: {self.utilization_rate():.1f}%

Decisions:
- Fully Funded: {self.num_fully_funded}
- Partially Funded: {self.num_partially_funded}
- Rejected: {self.num_rejected}

Impact:
- Total People Benefitted: {self.total_people_benefitted:,}
- Average Efficiency Ratio: {self.average_efficiency_ratio:.1%}
"""
