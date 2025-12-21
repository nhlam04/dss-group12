from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum
import numpy as np
from datetime import datetime


class ProgramCategory(Enum):
    """Các loại chương trình từ thiện"""
    HEALTHCARE = "Y tế"
    EDUCATION = "Giáo dục"
    FOOD_SECURITY = "Thực phẩm"
    DISASTER_RELIEF = "H trợ thiên tai"
    HOUSING = "Nhà ở"
    ENVIRONMENT = "Môi trường"
    OTHER = "Khác"


class UrgencyLevel(Enum):
    """Tính cấp bách"""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    FLEXIBLE = 1


@dataclass
class CharityAgent:
    """Tổ chức yêu cầu từ thiện"""
    agent_id: str
    name: str
    transparency_score: float
    total_programs_completed: int
    programs_succeeded: int
    
    @property
    def success_rate(self) -> float:
        """Tính toán mức độ hoàn thành"""
        if self.total_programs_completed == 0:
            return 0.0
        return self.programs_succeeded / self.total_programs_completed
    
    def __post_init__(self):
        if self.total_programs_completed < 0:
            raise ValueError("Số lượng chương trình không thể là số âm")
        if self.programs_succeeded < 0:
            raise ValueError("Số chương trình thành coong không thể là số âm")
        if self.programs_succeeded > self.total_programs_completed:
            raise ValueError("Số chương trình thành công không thể vượt quá số lượng chương trình")
        if not (0 <= self.transparency_score <= 1):
            raise ValueError("mức độ minh bạch phải là giá trị giữa 0 và 1")


@dataclass
class GrantRequest:
    request_id: str
    agent: CharityAgent
    program_name: str
    amount_requested: float
    overhead_cost: float
    people_benefitted: int
    duration_months: int
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
            raise ValueError("Yêu cầu không thể âm")
        if self.overhead_cost < 0:
            raise ValueError("Chi phí không thể âm")
        if self.overhead_cost >= self.amount_requested:
            raise ValueError("Chi phí không thể vượt quá yêu cầu")
        if self.people_benefitted <= 0:
            raise ValueError("Số người hưởng lợi không thể âm")
        if self.duration_months <= 0:
            raise ValueError("Thời lượng không th âm")
        if not (0 <= self.sustainability_score <= 1):
            raise ValueError("Độ bền vững là giá trị giữa 0 và 1")
        if self.status not in ['pending', 'funded', 'rejected', 'completed']:
            raise ValueError("Trạng thái phải là 'pending', 'funded', 'rejected', hoặc 'completed'")
        
        self.net_charity_amount = self.amount_requested - self.overhead_cost
        self.overhead_ratio = self.overhead_cost / self.amount_requested
    
    def cost_per_person(self) -> float:
        return self.amount_requested / self.people_benefitted
    
    def net_cost_per_person(self) -> float:
        return self.net_charity_amount / self.people_benefitted
    
    def monthly_impact(self) -> float:
        return self.people_benefitted / self.duration_months
    
    def efficiency_ratio(self) -> float:
        return 1 - self.overhead_ratio
    
    def risk_adjusted_benefit(self) -> float:
        return self.people_benefitted * self.agent.success_rate


@dataclass
class AllocationDecision:
    """Phân bổ tiền"""
    request: GrantRequest
    amount_allocated: float
    allocation_percentage: float
    priority_score: float
    rank: int
    rationale: str
    
    def is_fully_funded(self) -> bool:
        return self.allocation_percentage >= 0.99
    
    def is_partially_funded(self) -> bool:
        return 0 < self.allocation_percentage < 0.99
    
    def is_rejected(self) -> bool:
        return self.allocation_percentage == 0


@dataclass
class FundAllocationResult:
    """Kết quả phân bổ"""
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
        return (self.total_allocated / self.total_budget) * 100
    
    def summary(self) -> str:
        return f"""
Tổng kết phân ổ:
------------------------
Tổng quỹ: ${self.total_budget:,.2f}
Tổng phân bổ: ${self.total_allocated:,.2f}
Còn dư: ${self.remaining_budget:,.2f}
Hiệu quả: {self.utilization_rate():.1f}%

Quyết định:
- Từ thiện hoàn toàn: {self.num_fully_funded}
- Từ thiện một phần: {self.num_partially_funded}
- Từ chối: {self.num_rejected}

Mức độ ảnh hưởng:
- Số người hưởng lợi: {self.total_people_benefitted:,}
- Hiệu quả trung bình: {self.average_efficiency_ratio:.1%}
"""
