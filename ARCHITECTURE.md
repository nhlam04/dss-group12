# System Architecture Diagram

## Overall System Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           INPUT DATA                                     │
└───────────────────────────┬─────────────────────────────────────────────┘
                            │
                ┌───────────┴──────────┐
                │                      │
        ┌───────▼────────┐    ┌───────▼────────┐
        │ CharityAgent   │    │  GrantRequest  │
        ├────────────────┤    ├────────────────┤
        │ • Name         │◄───┤ • Program Info │
        │ • Success Rate │    │ • Amount       │
        │ • Transparency │    │ • Beneficiaries│
        │ • Track Record │    │ • Duration     │
        └────────────────┘    │ • Category     │
                              │ • Urgency      │
                              └───────┬────────┘
                                      │
                            ┌─────────▼──────────┐
                            │  TOPSIS Analyzer   │
                            ├────────────────────┤
                            │  Multi-Criteria    │
                            │  Evaluation:       │
                            │                    │
                            │  1. Extract Matrix │
                            │  2. Normalize      │
                            │  3. Apply Weights  │
                            │  4. Find Ideal     │
                            │  5. Calculate Dist │
                            │  6. Compute Scores │
                            └─────────┬──────────┘
                                      │
                            ┌─────────▼──────────┐
                            │   Ranked Requests  │
                            │   with Priority    │
                            │   Scores (0-1)     │
                            └─────────┬──────────┘
                                      │
                ┌─────────────────────┼─────────────────────┐
                │                     │                     │
        ┌───────▼────────┐  ┌────────▼────────┐  ┌────────▼────────┐
        │ Greedy Alloc   │  │ Proportional    │  │ Knapsack Opt   │
        ├────────────────┤  ├─────────────────┤  ├─────────────────┤
        │ Fund top ranks │  │ Distribute by   │  │ Dynamic Prog   │
        │ until budget   │  │ score ratios    │  │ Maximize value │
        │ exhausted      │  │ Reserve option  │  │ Subject to     │
        │ Allow partial? │  │ Min threshold   │  │ budget         │
        └───────┬────────┘  └────────┬────────┘  └────────┬────────┘
                │                    │                     │
                └────────────────────┼─────────────────────┘
                                     │
                        ┌────────────▼───────────┐
                        │ AllocationDecision(s) │
                        ├────────────────────────┤
                        │ • Request              │
                        │ • Amount Allocated     │
                        │ • Percentage           │
                        │ • Priority Score       │
                        │ • Rank                 │
                        │ • Rationale            │
                        └────────────┬───────────┘
                                     │
                        ┌────────────▼───────────┐
                        │ FundAllocationResult  │
                        ├────────────────────────┤
                        │ • Total Budget         │
                        │ • Total Allocated      │
                        │ • Remaining Budget     │
                        │ • All Decisions        │
                        │ • Impact Metrics       │
                        └────────────┬───────────┘
                                     │
                ┌────────────────────┼────────────────────┐
                │                    │                    │
        ┌───────▼────────┐  ┌────────▼────────┐  ┌──────▼──────┐
        │ Text Reports   │  │ Visualizations  │  │ JSON Export │
        ├────────────────┤  ├─────────────────┤  ├─────────────┤
        │ • Summary      │  │ • Pie Charts    │  │ • Structured│
        │ • Decisions    │  │ • Bar Charts    │  │ • API Ready │
        │ • Comparisons  │  │ • Scatter Plots │  │ • Database  │
        └────────────────┘  └─────────────────┘  └─────────────┘
```

## TOPSIS Algorithm Detail

```
┌─────────────────────────────────────────────────────────────┐
│                    TOPSIS PROCESS                           │
└─────────────────────────────────────────────────────────────┘

Step 1: CREATE DECISION MATRIX
┌─────────────────────────────────────────────────────────────┐
│          C1      C2      C3      C4      C5      C6      C7 │
│ Req 1 │ 5000    0.90    0.92    27.00   4       0.85    0.95│
│ Req 2 │ 500     0.85    0.88    136.00  3       0.90    0.90│
│ Req 3 │ 10000   0.90    0.85    18.00   5       0.40    0.85│
│  ...  │  ...     ...     ...     ...    ...     ...     ... │
└─────────────────────────────────────────────────────────────┘
         ↓
Step 2: NORMALIZE (Vector Normalization)
         r_ij = x_ij / sqrt(sum(x_ij^2))
         ↓
Step 3: APPLY WEIGHTS
┌─────────────────────────────────────────────────────────────┐
│ Weights: 0.25   0.20    0.15    0.15    0.10    0.10    0.05│
│          ↓       ↓       ↓       ↓       ↓       ↓       ↓  │
│ Weighted Matrix: v_ij = w_j × r_ij                         │
└─────────────────────────────────────────────────────────────┘
         ↓
Step 4: IDEAL SOLUTIONS
┌─────────────────────────────────────────────────────────────┐
│ Ideal Best  (A+): │ max(v_1), max(v_2), ..., max(v_n)      │
│ Ideal Worst (A-): │ min(v_1), min(v_2), ..., min(v_n)      │
└─────────────────────────────────────────────────────────────┘
         ↓
Step 5: CALCULATE DISTANCES
┌─────────────────────────────────────────────────────────────┐
│ Distance to Best:  S+ = sqrt(Σ(v_ij - v_j+)^2)            │
│ Distance to Worst: S- = sqrt(Σ(v_ij - v_j-)^2)            │
└─────────────────────────────────────────────────────────────┘
         ↓
Step 6: CLOSENESS COEFFICIENT (Priority Score)
┌─────────────────────────────────────────────────────────────┐
│           C = S- / (S+ + S-)                                │
│           Range: [0, 1]                                     │
│           Higher = Better (closer to ideal)                 │
└─────────────────────────────────────────────────────────────┘
         ↓
Step 7: RANK BY SCORE
┌─────────────────────────────────────────────────────────────┐
│ Rank 1: Request with highest C value                       │
│ Rank 2: Request with 2nd highest C value                   │
│  ...                                                         │
└─────────────────────────────────────────────────────────────┘
```

## Allocation Strategies Comparison

```
┌────────────────────────────────────────────────────────────────────┐
│                    GREEDY (FULL FUNDING)                           │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Budget: $500,000                                                  │
│  ┌──────────┐                                                      │
│  │ Rank #1  │  $200k → ✓ FUNDED ($200k)                           │
│  │ Score:.90│  Budget Remaining: $300k                            │
│  └──────────┘                                                      │
│  ┌──────────┐                                                      │
│  │ Rank #2  │  $150k → ✓ FUNDED ($150k)                           │
│  │ Score:.53│  Budget Remaining: $150k                            │
│  └──────────┘                                                      │
│  ┌──────────┐                                                      │
│  │ Rank #3  │  $120k → ✓ FUNDED ($120k)                           │
│  │ Score:.30│  Budget Remaining: $30k                             │
│  └──────────┘                                                      │
│  ┌──────────┐                                                      │
│  │ Rank #4  │  $300k → ✗ REJECTED (insufficient budget)           │
│  │ Score:.29│  Budget Remaining: $30k                             │
│  └──────────┘                                                      │
│                                                                    │
│  Result: 3 funded, 5 rejected, $30k remaining                     │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                  GREEDY (PARTIAL ALLOWED)                          │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Same as above, but Rank #5 gets:                                 │
│  ┌──────────┐                                                      │
│  │ Rank #5  │  $45k requested                                     │
│  │ Score:.25│  → ◐ PARTIAL ($30k = 67%)                           │
│  └──────────┘  Budget Remaining: $0                               │
│                                                                    │
│  Result: 3 full, 1 partial, 4 rejected, $0 remaining              │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                    PROPORTIONAL                                    │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Allocate proportional to scores (with 10% reserve)               │
│  Available: $450k (90% of $500k)                                  │
│                                                                    │
│  Total Score = 2.5                                                │
│  Rank #1 (Score 0.90): 0.90/2.5 × $450k = $162k                  │
│  Rank #2 (Score 0.53): 0.53/2.5 × $450k = $95k                   │
│  Rank #3 (Score 0.30): 0.30/2.5 × $450k = $54k                   │
│  ...                                                               │
│                                                                    │
│  Result: More programs get funding, but amounts vary              │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                    KNAPSACK (0/1)                                  │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Find optimal combination to maximize:                            │
│    Value = People × SuccessRate × (1 - OverheadRatio)            │
│                                                                    │
│  Dynamic Programming Table:                                       │
│  ┌──────┬──────┬──────┬──────┬──────┬──────┐                     │
│  │Item  │Cost  │Value │Include?                │                 │
│  ├──────┼──────┼──────┼────────────────────────┤                 │
│  │Req 1 │$200k │7650  │ ✓ YES                  │                 │
│  │Req 2 │$150k │3740  │ ✓ YES                  │                 │
│  │Req 3 │$120k │2090  │ ✓ YES                  │                 │
│  │Req 4 │$300k │1989  │ ✗ NO (would exceed)    │                 │
│  └──────┴──────┴──────┴────────────────────────┘                 │
│                                                                    │
│  Result: Mathematically optimal impact                            │
└────────────────────────────────────────────────────────────────────┘
```

## Criteria Evaluation Detail

```
┌─────────────────────────────────────────────────────────────────┐
│                   EVALUATING A GRANT REQUEST                    │
└─────────────────────────────────────────────────────────────────┘

Example: "Emergency Food Distribution"
─────────────────────────────────────────────────────────────────

Input Data:
  • Amount Requested: $200,000
  • Overhead Cost: $20,000
  • People Benefitted: 10,000
  • Duration: 6 months
  • Success Rate: 0.85 (85%)
  • Urgency: CRITICAL (5)
  • Sustainability: 0.40 (40%)
  • Transparency: 0.85 (85%)

Calculated Metrics:
  ┌────────────────────────────────────────────────────┐
  │ Net Amount = $200k - $20k = $180,000              │
  │ Overhead Ratio = $20k / $200k = 10%               │
  │ Efficiency = 1 - 0.10 = 90%                       │
  │ Cost/Person = $200k / 10,000 = $20.00             │
  │ Net Cost/Person = $180k / 10,000 = $18.00         │
  │ Monthly Impact = 10,000 / 6 = 1,667 people/month  │
  └────────────────────────────────────────────────────┘

TOPSIS Evaluation (after normalization & weighting):
  ┌────────────────────────────────────────────────────┐
  │ 1. People (25% × normalized) → High contribution   │
  │ 2. Efficiency (20% × 0.90) → High contribution     │
  │ 3. Success (15% × 0.85) → Good contribution        │
  │ 4. Cost-Eff (15% × inverted) → Excellent           │
  │ 5. Urgency (10% × 5/5) → Maximum                   │
  │ 6. Sustain (10% × 0.40) → Low contribution         │
  │ 7. Transparency (5% × 0.85) → Good                 │
  └────────────────────────────────────────────────────┘

Final Priority Score: 0.9033 → RANK #1
```

## File Dependencies

```
requirements.txt
    │
    ├─► numpy (numerical computations)
    ├─► pandas (data manipulation)  
    └─► matplotlib (visualizations)

charity_decision_system.py (Core Data Models)
    │
    ├─► CharityAgent
    ├─► GrantRequest
    ├─► AllocationDecision
    └─► FundAllocationResult

topsis_analyzer.py
    │
    ├─► imports: charity_decision_system
    └─► TOPSISAnalyzer

fund_allocator.py
    │
    ├─► imports: charity_decision_system, topsis_analyzer
    └─► FundAllocator

example_usage.py
    │
    ├─► imports: charity_decision_system, fund_allocator, topsis_analyzer
    └─► Sample data generators & demonstrations

interactive_cli.py
    │
    ├─► imports: charity_decision_system, fund_allocator, topsis_analyzer
    └─► CLI interface

visualizations.py
    │
    ├─► imports: charity_decision_system, matplotlib
    └─► AllocationVisualizer

quickstart.py
    │
    └─► imports: example_usage
```

## Typical Workflow

```
START
  │
  ▼
┌────────────────────┐
│ Gather Input Data  │
│ • Agents           │
│ • Requests         │
│ • Budget           │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Create Objects     │
│ CharityAgent(...)  │
│ GrantRequest(...)  │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Initialize         │
│ FundAllocator      │
│ with budget        │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐      ┌─────────────────┐
│ Choose Strategy    │──────┤ • Greedy        │
│                    │      │ • Proportional  │
│                    │      │ • Knapsack      │
└─────────┬──────────┘      └─────────────────┘
          │
          ▼
┌────────────────────┐
│ Execute Allocation │
│ result = allocate()│
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Review Results     │
│ • Summary          │
│ • Decisions        │
│ • Metrics          │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Output             │
│ • Print            │
│ • Visualize        │
│ • Export JSON      │
└────────────────────┘
  │
  ▼
END
```
