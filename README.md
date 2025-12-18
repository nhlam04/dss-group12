# Charity Fund Decision Support System

A sophisticated multi-criteria decision-making system that helps charity funds allocate resources to grant requests using TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution) ranking and various optimization algorithms.

## Overview

This system helps charity fund managers make data-driven decisions about how to distribute limited funds among multiple grant requests by:

1. **Ranking** grant requests using multi-criteria analysis (TOPSIS)
2. **Optimizing** fund allocation using different strategies
3. **Maximizing** overall impact while respecting budget constraints

## Key Features

### Multi-Criteria Evaluation
The system evaluates grant requests based on:
- **People Benefitted** (25% weight) - Scale of impact
- **Efficiency** (20% weight) - Low overhead ratio
- **Success Rate** (15% weight) - Agent's historical track record
- **Cost Effectiveness** (15% weight) - Cost per person benefitted
- **Urgency** (10% weight) - Time sensitivity of the program
- **Sustainability** (10% weight) - Long-term value creation
- **Transparency** (5% weight) - Agent's accountability score

### Allocation Strategies

1. **Greedy Allocation** - Funds highest-priority requests first until budget exhausted
   - Supports full or partial funding
   - Simple and intuitive

2. **Proportional Allocation** - Distributes budget proportional to TOPSIS scores
   - Ensures all high-scoring requests receive some funding
   - Allows setting a reserve ratio

3. **Knapsack Optimization** - Selects optimal combination to maximize impact
   - Uses dynamic programming
   - Only fully funds or rejects (no partial funding)
   - Maximizes: people_benefitted × success_rate × efficiency

## System Architecture

```
charity_decision_system.py    # Core data models
├── CharityAgent              # Organization requesting funds
├── GrantRequest              # Individual program funding request
├── AllocationDecision        # Funding decision for one request
└── FundAllocationResult      # Overall allocation outcome

topsis_analyzer.py            # Multi-criteria ranking
└── TOPSISAnalyzer           # Implements TOPSIS algorithm

fund_allocator.py             # Allocation optimization
└── FundAllocator            # Implements allocation strategies

example_usage.py              # Demonstration & examples
```

## Installation

```bash
pip install numpy pandas
```

## Quick Start

```python
from charity_decision_system import CharityAgent, GrantRequest, ProgramCategory, UrgencyLevel
from fund_allocator import FundAllocator

# Create a charity agent
agent = CharityAgent(
    agent_id="A001",
    name="Global Health Initiative",
    success_rate=0.92,
    transparency_score=0.95,
    total_programs_completed=50,
    programs_succeeded=46
)

# Create a grant request
request = GrantRequest(
    request_id="R001",
    agent=agent,
    program_name="Malaria Prevention in Rural Africa",
    amount_requested=150000,
    overhead_cost=15000,
    people_benefitted=5000,
    duration_months=12,
    category=ProgramCategory.HEALTHCARE,
    urgency=UrgencyLevel.HIGH,
    geographic_location="Sub-Saharan Africa",
    sustainability_score=0.85
)

# Allocate funds
allocator = FundAllocator(total_budget=500000)
result = allocator.allocate_greedy([request], allow_partial=True)

print(result.summary())
```

## Running the Example

```bash
python example_usage.py
```

This will demonstrate:
- TOPSIS ranking of 8 sample grant requests
- Greedy allocation with partial funding
- Proportional allocation
- Knapsack optimization
- Side-by-side comparison of all strategies

## Grant Request Information

Each grant request includes:

**Required Fields:**
- `amount_requested` - Total funding needed
- `overhead_cost` - Administrative costs (non-charity expenses)
- `people_benefitted` - Number of people impacted
- `duration_months` - Time to complete the program
- `category` - Type of program (Healthcare, Education, etc.)
- `urgency` - Priority level (Critical, High, Medium, Low, Flexible)
- `geographic_location` - Where the program operates
- `sustainability_score` - Long-term impact score (0-1)

**Agent Information:**
- `success_rate` - Historical success rate (0-1)
- `transparency_score` - Accountability rating (0-1)
- Previous program track record

## Optimization Objective

The system maximizes **Cost-Effectiveness Weighted Impact**:

$$\text{Maximize} \sum_{i=1}^{n} x_i \cdot \text{People}_i \cdot \text{SuccessRate}_i \cdot (1 - \text{Overhead}_i)$$

Subject to:
$$\sum_{i=1}^{n} x_i \cdot \text{Amount}_i \leq \text{Budget}$$

Where $x_i \in [0,1]$ is the allocation percentage for request $i$.

## Customization

### Adjusting Criteria Weights

```python
from topsis_analyzer import TOPSISAnalyzer

custom_weights = {
    'people_benefitted': 0.30,
    'efficiency': 0.25,
    'success_rate': 0.20,
    'cost_effectiveness': 0.10,
    'urgency': 0.10,
    'sustainability': 0.03,
    'transparency': 0.02,
}

analyzer = TOPSISAnalyzer(weights=custom_weights)
```

### Setting Minimum Allocation Threshold

```python
# Only fund requests if we can provide at least 70% of requested amount
allocator = FundAllocator(
    total_budget=500000,
    min_allocation_percentage=0.70
)
```

## Output Interpretation

### Priority Score
- Range: 0 to 1 (higher is better)
- Represents closeness to ideal solution across all criteria
- Used to rank requests

### Allocation Percentage
- 100%: Fully funded
- 50-99%: Partially funded
- 0%: Rejected

### Efficiency Ratio
- Percentage of funds going directly to beneficiaries
- Formula: (Amount - Overhead) / Amount
- Higher is better (less overhead)

## Use Cases

1. **Grant-making foundations** distributing annual budgets
2. **Corporate social responsibility** programs allocating CSR funds
3. **Government agencies** distributing social welfare budgets
4. **Non-profit coalitions** coordinating resource allocation
5. **Emergency response** prioritizing disaster relief efforts

## Advantages of TOPSIS

- Handles multiple conflicting criteria objectively
- Transparent and explainable decisions
- Flexible weighting system
- Considers both positive and negative ideal solutions
- Well-established mathematical foundation

## License

MIT License - Feel free to use and modify for your charity allocation needs.

## Contributing

Suggestions for additional criteria or allocation strategies are welcome!

## Future Enhancements

- Web-based dashboard for interactive decision-making
- Machine learning to predict program success rates
- Geographic diversity constraints
- Multi-period allocation planning
- Risk analysis and sensitivity testing
- Integration with grant management systems
