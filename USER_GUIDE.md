# Charity Fund Decision Support System - User Guide

## Table of Contents
1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [System Components](#system-components)
4. [Usage Examples](#usage-examples)
5. [Understanding the Results](#understanding-the-results)
6. [Customization](#customization)
7. [FAQ](#faq)

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `numpy` - For numerical computations
- `pandas` - For data manipulation
- `matplotlib` - For visualizations

## Quick Start

### Option 1: Run the Example

See the system in action with pre-loaded sample data:

```bash
python example_usage.py
```

This will:
- Show TOPSIS ranking of 8 sample programs
- Demonstrate different allocation strategies
- Compare all strategies side-by-side

### Option 2: Interactive CLI

Use the interactive command-line interface:

```bash
python interactive_cli.py
```

Features:
- Load sample data or input your own
- Choose allocation strategy
- Export results to JSON
- View detailed analysis

### Option 3: Python Script

```python
from charity_decision_system import CharityAgent, GrantRequest, ProgramCategory, UrgencyLevel
from fund_allocator import FundAllocator

# Create agent
agent = CharityAgent(
    agent_id="A001",
    name="Health First",
    success_rate=0.90,
    transparency_score=0.85,
    total_programs_completed=20,
    programs_succeeded=18
)

# Create request
request = GrantRequest(
    request_id="R001",
    agent=agent,
    program_name="Community Vaccination Drive",
    amount_requested=50000,
    overhead_cost=5000,
    people_benefitted=2000,
    duration_months=6,
    category=ProgramCategory.HEALTHCARE,
    urgency=UrgencyLevel.HIGH,
    geographic_location="Rural India",
    sustainability_score=0.70
)

# Allocate funds
allocator = FundAllocator(total_budget=100000)
result = allocator.allocate_greedy([request])

print(result.summary())
```

## System Components

### 1. Core Data Models (`charity_decision_system.py`)

**CharityAgent**: Organization requesting funds
- Tracks historical performance
- Success rate and transparency score
- Past program statistics

**GrantRequest**: Individual program funding request
- All program details (cost, beneficiaries, duration)
- Automatically calculates efficiency metrics
- Links to requesting agent

**AllocationDecision**: Funding decision outcome
- Amount allocated and percentage
- Priority ranking
- Rationale for decision

**FundAllocationResult**: Complete allocation summary
- Budget utilization
- Number of programs funded/rejected
- Impact metrics

### 2. TOPSIS Analyzer (`topsis_analyzer.py`)

Implements multi-criteria decision analysis:
- Ranks requests using 7 weighted criteria
- Calculates similarity to ideal solution
- Provides explainable scoring

**Default Criteria Weights:**
- People Benefitted: 25%
- Efficiency (low overhead): 20%
- Success Rate: 15%
- Cost Effectiveness: 15%
- Urgency: 10%
- Sustainability: 10%
- Transparency: 5%

### 3. Fund Allocator (`fund_allocator.py`)

Implements allocation strategies:

**Greedy Allocation**
- Funds highest-priority requests first
- Can allow partial funding
- Simple and intuitive

**Proportional Allocation**
- Distributes budget proportional to scores
- Ensures high-scoring requests get something
- Can set reserve ratio

**Knapsack Optimization**
- Finds optimal combination
- Maximizes total impact
- Only fully funds (no partial)

### 4. Visualizations (`visualizations.py`)

Creates charts and dashboards:
- Budget utilization pie charts
- Decision breakdown bar charts
- Efficiency vs impact scatter plots
- Strategy comparisons

### 5. Interactive CLI (`interactive_cli.py`)

User-friendly command-line interface:
- Input custom data
- Run analyses
- Export results

## Usage Examples

### Example 1: Basic Allocation

```python
from example_usage import create_sample_requests
from fund_allocator import FundAllocator

requests = create_sample_requests()
allocator = FundAllocator(total_budget=500000)

# Greedy allocation with partial funding allowed
result = allocator.allocate_greedy(requests, allow_partial=True)
print(result.summary())
```

### Example 2: Custom Criteria Weights

```python
from topsis_analyzer import TOPSISAnalyzer

# Emphasize urgency and transparency
custom_weights = {
    'people_benefitted': 0.20,
    'efficiency': 0.15,
    'success_rate': 0.15,
    'cost_effectiveness': 0.10,
    'urgency': 0.25,  # Increased
    'sustainability': 0.05,
    'transparency': 0.10,  # Increased
}

analyzer = TOPSISAnalyzer(weights=custom_weights)
ranked = analyzer.rank_requests(requests)
```

### Example 3: Compare All Strategies

```python
allocator = FundAllocator(total_budget=500000)
results = allocator.compare_strategies(requests)

for strategy, result in results.items():
    print(f"\n{strategy}:")
    print(f"  People Benefitted: {result.total_people_benefitted:,}")
    print(f"  Utilization: {result.utilization_rate():.1f}%")
```

### Example 4: Export to JSON

```python
import json

# Run allocation
result = allocator.allocate_greedy(requests)

# Export
output = {
    'total_allocated': result.total_allocated,
    'people_benefitted': result.total_people_benefitted,
    'decisions': [
        {
            'program': d.request.program_name,
            'allocated': d.amount_allocated,
            'rank': d.rank
        }
        for d in result.decisions
    ]
}

with open('results.json', 'w') as f:
    json.dump(output, f, indent=2)
```

### Example 5: Visualizations

```python
from visualizations import AllocationVisualizer
import matplotlib.pyplot as plt

viz = AllocationVisualizer()

# Create overview dashboard
viz.plot_allocation_overview(result, "My Allocation Analysis")

# Compare strategies visually
results = allocator.compare_strategies(requests)
viz.plot_strategy_comparison(results)

plt.show()
```

## Understanding the Results

### Priority Score
- **Range**: 0.0 to 1.0
- **Meaning**: Closeness to ideal solution across all criteria
- **Higher is Better**: 1.0 would be perfect on all criteria

**Interpretation:**
- 0.8-1.0: Excellent - High priority
- 0.5-0.8: Good - Medium priority
- 0.2-0.5: Fair - Lower priority
- 0.0-0.2: Poor - May be rejected

### Allocation Percentage
- **100%**: Fully funded - Request completely satisfied
- **50-99%**: Partially funded - Some funding provided
- **0%**: Rejected - No funding allocated

### Efficiency Ratio
Formula: `(Amount - Overhead) / Amount`

**Example:**
- Request: $100,000
- Overhead: $15,000
- Efficiency: 85% ($85,000 goes to beneficiaries)

**Good Practice:**
- >90%: Excellent efficiency
- 80-90%: Good efficiency
- 70-80%: Acceptable
- <70%: High overhead (flag for review)

### Budget Utilization
Percentage of total budget allocated:

- **100%**: All funds allocated
- **90-99%**: Nearly all funds used
- **<90%**: Significant funds remaining

**Note:** Lower utilization may indicate:
- Minimum allocation thresholds not met
- Proportional strategy with reserve
- Limited high-quality requests

## Customization

### Adjust Minimum Allocation Threshold

Only fund if you can provide at least X% of request:

```python
# Only fund if can provide 75% or more
allocator = FundAllocator(
    total_budget=500000,
    min_allocation_percentage=0.75
)
```

### Change Urgency Values

Modify urgency impact by editing `UrgencyLevel` enum values:

```python
class UrgencyLevel(Enum):
    CRITICAL = 10  # Double the impact
    HIGH = 5
    MEDIUM = 3
    LOW = 1
    FLEXIBLE = 1
```

### Add New Program Categories

Extend `ProgramCategory`:

```python
class ProgramCategory(Enum):
    # Existing categories...
    MENTAL_HEALTH = "Mental Health"
    ANIMAL_WELFARE = "Animal Welfare"
    ARTS_CULTURE = "Arts & Culture"
```

### Create Custom Allocation Strategy

```python
class FundAllocator:
    def allocate_custom(self, requests):
        # Your custom logic here
        # Must return FundAllocationResult
        pass
```

## FAQ

### Q: How does TOPSIS ranking work?
**A:** TOPSIS calculates the Euclidean distance of each request to both an ideal best solution (maximum on all criteria) and an ideal worst solution (minimum on all criteria). Requests closer to the best and farther from the worst get higher scores.

### Q: Which allocation strategy should I use?
**A:** 
- **Greedy**: When you want to fully fund as many high-priority programs as possible
- **Proportional**: When you want to distribute funding more evenly among good programs
- **Knapsack**: When you want to mathematically optimize total impact

### Q: Can I handle thousands of requests?
**A:** Yes, but the knapsack algorithm may be slow for very large numbers. For 1000+ requests:
- Use Greedy or Proportional strategies
- Pre-filter obviously unsuitable requests
- Consider batch processing

### Q: How do I handle multi-year funding?
**A:** You can:
1. Run allocation separately for each year
2. Adjust `duration_months` to reflect the annual portion
3. Create separate requests for each year of a multi-year program

### Q: What if two requests have identical scores?
**A:** The tiebreaker is their original order in the list. For deterministic ordering, sort by a secondary criterion first (e.g., request_id).

### Q: Can I weight different agents differently?
**A:** Not directly, but you can:
1. Adjust the agent's `transparency_score` or `success_rate`
2. Modify the criteria weights to emphasize these factors
3. Pre-filter requests by agent category

### Q: How do I handle emergency/disaster situations?
**A:** 
1. Set `urgency=UrgencyLevel.CRITICAL`
2. Increase the urgency weight in criteria
3. Use a separate allocation run for emergencies with reserved funds

### Q: Can partial funding harm a program?
**A:** This depends on the program. The system allows setting `min_allocation_percentage` to ensure programs receive enough funding to be viable. Alternatively, use the Greedy (Full Funding) or Knapsack strategies that don't partial-fund.

### Q: How do I validate my data?
**A:** The system automatically validates:
- Positive amounts and counts
- Overhead < total amount
- Scores between 0 and 1
- Success rate matches program counts

ValueError will be raised for invalid data.

### Q: Can I integrate this with a database?
**A:** Yes! Create a data loader:

```python
def load_requests_from_db(connection):
    # Query database
    rows = connection.execute("SELECT * FROM grant_requests")
    
    requests = []
    for row in rows:
        agent = CharityAgent(...)  # Map from row
        request = GrantRequest(...)
        requests.append(request)
    
    return requests
```

### Q: How accurate are the results?
**A:** The system provides mathematically sound rankings and allocations based on the criteria and weights you specify. Accuracy depends on:
- Quality of input data
- Appropriateness of criteria weights for your context
- Realistic success rate estimates

### Q: Can I use this for non-charity allocations?
**A:** Yes! The system can be adapted for:
- Research grant allocation
- Scholarship distribution
- Investment portfolio selection
- Resource allocation in businesses
- Project prioritization

Just rename classes and adjust criteria to fit your domain.

## Support

For issues, questions, or contributions:
1. Check this guide
2. Review the code documentation
3. Examine `example_usage.py` for patterns
4. Create an issue or pull request

## License

MIT License - Free to use and modify for your needs.
