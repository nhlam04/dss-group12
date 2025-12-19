# Input Metrics Classification

## Objective Metrics
**Measurable without human judgment - factual data**

### Grant Requests
| Metric | Description | Unit | Why Objective |
|--------|-------------|------|---------------|
| Amount Requested | Total funding requested | $ (dollars) | Direct financial amount |
| Overhead Cost | Non-charity administrative costs | $ (dollars) | Direct financial amount |
| People Benefitted | Number of people impacted | Count | Quantifiable estimate |
| Duration | Project timeline | Months | Measurable timeframe |

### Charity Agents
| Metric | Description | Unit | Why Objective |
|--------|-------------|------|---------------|
| Total Programs Completed | Historical count of all programs | Count | Factual count |
| Programs Succeeded | Count of successful programs | Count | Factual count |
| Success Rate | Calculated percentage | % | Mathematical calculation |

---

## Subjective Metrics
**Require human evaluation and judgment**

### Grant Requests
| Metric | Description | Range/Options | Why Subjective |
|--------|-------------|---------------|----------------|
| Category | Type of charity program | Healthcare, Education, Food Security, Disaster Relief, Housing, Environment, Other | Requires classification and interpretation |
| Urgency Level | Priority assessment | Critical (5), High (4), Medium (3), Low (2), Flexible (1) | Requires human judgment of need |
| Sustainability Score | Long-term impact evaluation | 0-1 scale | Requires expert assessment of future outcomes |

### Charity Agents
| Metric | Description | Range | Why Subjective |
|--------|-------------|-------|----------------|
| Transparency Score | Reporting quality evaluation | 0-1 scale | Requires human evaluation of accountability practices |

---

## TOPSIS Criteria Breakdown

The decision algorithm uses 7 weighted criteria. Here's how they relate to the input metrics:

| TOPSIS Criterion | Weight | Based On | Type |
|-----------------|--------|----------|------|
| People Benefitted | 25% | Direct input | Objective |
| Efficiency | 20% | people_benefitted / duration_months | Calculated from Objective |
| Success Rate | 15% | programs_succeeded / total_programs_completed | Calculated from Objective |
| Cost Effectiveness | 15% | people_benefitted / amount_requested | Calculated from Objective |
| Urgency | 10% | Direct input (urgency level) | Subjective |
| Sustainability | 10% | Direct input (sustainability score) | Subjective |
| Transparency | 5% | Direct input (transparency score) | Subjective |

**Key Insight:** 75% of the decision weight is based on objective/calculated metrics, while 25% is based on subjective human evaluation.

---

## Data Entry Guidelines

### For Objective Metrics:
✓ Use precise measurements when possible  
✓ Base on historical data or documented estimates  
✓ Be consistent with units and definitions  
✓ Update automatically when new information is available  

### For Subjective Metrics:
✓ Establish clear evaluation criteria  
✓ Use the same evaluator for consistency  
✓ Document the reasoning for scores  
✓ Review and calibrate periodically  
✓ Consider using rubrics or scoring guides  

---

## Example Evaluation

**Objective Data:**
```
Amount Requested: $50,000 (from budget)
Overhead Cost: $5,000 (10% administrative, from budget breakdown)
People Benefitted: 1,000 (estimated beneficiaries, from project plan)
Duration: 12 months (project timeline)
Total Programs Completed: 15 (historical count)
Programs Succeeded: 12 (historical count, 80% success rate)
```

**Subjective Evaluation:**
```
Category: HEALTHCARE (evaluator classifies type of program)
Urgency: HIGH (4) (evaluator assesses time sensitivity)
Sustainability: 0.7 (evaluator judges long-term impact potential)
Transparency: 0.85 (evaluator reviews reporting quality, audit history)
```

---

## Common Questions

**Q: Is "People Benefitted" really objective?**  
A: While it involves estimation, it's based on quantifiable project plans and comparable historical data, making it more objective than subjective. The key is using a consistent methodology.

**Q: Why is Transparency subjective?**  
A: It requires human judgment to evaluate reporting quality, financial disclosure, audit results, and accountability practices. Different evaluators might score it differently.

**Q: Can we make Urgency more objective?**  
A: You could create a rubric (e.g., "disaster relief = 5, ongoing programs = 2"), but the initial classification still requires judgment about the situation's severity.

**Q: How often should subjective metrics be re-evaluated?**  
A: Transparency scores should be updated annually or when new audits are available. Urgency and sustainability should be assessed for each new request based on current conditions.
