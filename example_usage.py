"""
Example Usage of Charity Fund Decision Support System
Demonstrates how to use the system with sample data
"""

from charity_decision_system import (
    CharityAgent, GrantRequest, ProgramCategory, UrgencyLevel
)
from fund_allocator import FundAllocator
from topsis_analyzer import TOPSISAnalyzer
import pandas as pd


def create_sample_agents():
    """Create sample charity agents with different track records"""
    agents = [
        CharityAgent(
            agent_id="A001",
            name="Global Health Initiative",
            success_rate=0.92,
            transparency_score=0.95,
            total_programs_completed=50,
            programs_succeeded=46
        ),
        CharityAgent(
            agent_id="A002",
            name="Education for All",
            success_rate=0.88,
            transparency_score=0.90,
            total_programs_completed=30,
            programs_succeeded=26
        ),
        CharityAgent(
            agent_id="A003",
            name="Food Security Network",
            success_rate=0.85,
            transparency_score=0.85,
            total_programs_completed=40,
            programs_succeeded=34
        ),
        CharityAgent(
            agent_id="A004",
            name="Disaster Relief Coalition",
            success_rate=0.78,
            transparency_score=0.88,
            total_programs_completed=25,
            programs_succeeded=19
        ),
        CharityAgent(
            agent_id="A005",
            name="Community Housing Project",
            success_rate=0.82,
            transparency_score=0.75,
            total_programs_completed=15,
            programs_succeeded=12
        ),
    ]
    return agents


def create_sample_requests():
    """Create sample grant requests"""
    agents = create_sample_agents()
    
    requests = [
        GrantRequest(
            request_id="R001",
            agent=agents[0],
            program_name="Malaria Prevention in Rural Africa",
            amount_requested=150000,
            overhead_cost=15000,
            people_benefitted=5000,
            duration_months=12,
            category=ProgramCategory.HEALTHCARE,
            urgency=UrgencyLevel.HIGH,
            geographic_location="Sub-Saharan Africa",
            sustainability_score=0.85
        ),
        GrantRequest(
            request_id="R002",
            agent=agents[1],
            program_name="STEM Education for Underprivileged Children",
            amount_requested=80000,
            overhead_cost=12000,
            people_benefitted=500,
            duration_months=24,
            category=ProgramCategory.EDUCATION,
            urgency=UrgencyLevel.MEDIUM,
            geographic_location="Urban India",
            sustainability_score=0.90
        ),
        GrantRequest(
            request_id="R003",
            agent=agents[2],
            program_name="Emergency Food Distribution",
            amount_requested=200000,
            overhead_cost=20000,
            people_benefitted=10000,
            duration_months=6,
            category=ProgramCategory.FOOD_SECURITY,
            urgency=UrgencyLevel.CRITICAL,
            geographic_location="Yemen",
            sustainability_score=0.40
        ),
        GrantRequest(
            request_id="R004",
            agent=agents[3],
            program_name="Earthquake Relief Shelters",
            amount_requested=300000,
            overhead_cost=45000,
            people_benefitted=3000,
            duration_months=8,
            category=ProgramCategory.DISASTER_RELIEF,
            urgency=UrgencyLevel.CRITICAL,
            geographic_location="Nepal",
            sustainability_score=0.50
        ),
        GrantRequest(
            request_id="R005",
            agent=agents[4],
            program_name="Affordable Housing Development",
            amount_requested=500000,
            overhead_cost=75000,
            people_benefitted=200,
            duration_months=36,
            category=ProgramCategory.HOUSING,
            urgency=UrgencyLevel.LOW,
            geographic_location="Detroit, USA",
            sustainability_score=0.95
        ),
        GrantRequest(
            request_id="R006",
            agent=agents[0],
            program_name="Clean Water Access Program",
            amount_requested=120000,
            overhead_cost=10000,
            people_benefitted=2500,
            duration_months=18,
            category=ProgramCategory.HEALTHCARE,
            urgency=UrgencyLevel.HIGH,
            geographic_location="Bangladesh",
            sustainability_score=0.92
        ),
        GrantRequest(
            request_id="R007",
            agent=agents[1],
            program_name="Digital Literacy Training",
            amount_requested=60000,
            overhead_cost=9000,
            people_benefitted=800,
            duration_months=12,
            category=ProgramCategory.EDUCATION,
            urgency=UrgencyLevel.MEDIUM,
            geographic_location="Rural Brazil",
            sustainability_score=0.80
        ),
        GrantRequest(
            request_id="R008",
            agent=agents[2],
            program_name="Community Gardens Initiative",
            amount_requested=45000,
            overhead_cost=5000,
            people_benefitted=1200,
            duration_months=24,
            category=ProgramCategory.FOOD_SECURITY,
            urgency=UrgencyLevel.LOW,
            geographic_location="Urban Philippines",
            sustainability_score=0.88
        ),
    ]
    return requests


def print_ranking_analysis(requests):
    """Print TOPSIS ranking analysis"""
    print("=" * 80)
    print("TOPSIS MULTI-CRITERIA RANKING ANALYSIS")
    print("=" * 80)
    
    analyzer = TOPSISAnalyzer()
    ranked = analyzer.rank_requests(requests)
    
    print(f"\nAnalyzed {len(requests)} grant requests using weighted criteria:")
    print("\nCriteria Weights:")
    for criterion, weight in analyzer.weights.items():
        print(f"  - {criterion}: {weight:.1%}")
    
    print("\n" + "-" * 80)
    print("RANKING RESULTS")
    print("-" * 80)
    
    for request, score, rank in ranked:
        print(f"\nRank #{rank}: {request.program_name}")
        print(f"  Agent: {request.agent.name}")
        print(f"  Priority Score: {score:.4f}")
        print(f"  Amount Requested: ${request.amount_requested:,.0f}")
        print(f"  People Benefitted: {request.people_benefitted:,}")
        print(f"  Cost per Person: ${request.net_cost_per_person():.2f}")
        print(f"  Efficiency: {request.efficiency_ratio():.1%}")
        print(f"  Success Rate: {request.agent.success_rate:.1%}")
        print(f"  Urgency: {request.urgency.name}")
        print(f"  Sustainability: {request.sustainability_score:.1%}")
    
    print("\n" + "=" * 80)


def print_allocation_results(result, strategy_name):
    """Print allocation results"""
    print("\n" + "=" * 80)
    print(f"ALLOCATION STRATEGY: {strategy_name.upper()}")
    print("=" * 80)
    print(result.summary())
    
    print("\nDETAILED DECISIONS:")
    print("-" * 80)
    
    # Sort by rank
    sorted_decisions = sorted(result.decisions, key=lambda d: d.rank)
    
    for decision in sorted_decisions:
        status_symbol = "[FULL]" if decision.is_fully_funded() else "[PART]" if decision.is_partially_funded() else "[REJ]"
        
        print(f"\n{status_symbol} Rank #{decision.rank}: {decision.request.program_name}")
        print(f"   Requested: ${decision.request.amount_requested:,.0f}")
        print(f"   Allocated: ${decision.amount_allocated:,.0f} ({decision.allocation_percentage:.0%})")
        print(f"   Priority Score: {decision.priority_score:.4f}")
        print(f"   People Benefitted: {int(decision.request.people_benefitted * decision.allocation_percentage):,}")
        print(f"   Rationale: {decision.rationale}")
    
    print("\n" + "=" * 80)


def compare_all_strategies(requests, budget):
    """Compare all allocation strategies side by side"""
    allocator = FundAllocator(total_budget=budget, min_allocation_percentage=0.5)
    results = allocator.compare_strategies(requests)
    
    print("\n" + "=" * 80)
    print("STRATEGY COMPARISON")
    print("=" * 80)
    
    comparison_data = []
    for strategy_name, result in results.items():
        comparison_data.append({
            'Strategy': strategy_name,
            'Allocated': f"${result.total_allocated:,.0f}",
            'Utilization': f"{result.utilization_rate():.1f}%",
            'Fully Funded': result.num_fully_funded,
            'Partially Funded': result.num_partially_funded,
            'Rejected': result.num_rejected,
            'People Benefitted': f"{result.total_people_benefitted:,}",
            'Avg Efficiency': f"{result.average_efficiency_ratio:.1%}"
        })
    
    df = pd.DataFrame(comparison_data)
    print("\n" + df.to_string(index=False))
    print("\n" + "=" * 80)
    
    return results


def main():
    """Main demonstration"""
    print("\n")
    print("=" * 80)
    print(" " * 15 + "CHARITY FUND DECISION SUPPORT SYSTEM")
    print("=" * 80)
    
    # Create sample data
    requests = create_sample_requests()
    total_budget = 500000  # $500,000 available
    
    print(f"\nScenario: {len(requests)} grant requests competing for ${total_budget:,.0f}")
    print(f"Total requested: ${sum(r.amount_requested for r in requests):,.0f}")
    
    # Step 1: Show TOPSIS ranking
    print_ranking_analysis(requests)
    
    # Step 2: Demonstrate greedy allocation
    allocator = FundAllocator(total_budget=total_budget, min_allocation_percentage=0.5)
    result_greedy = allocator.allocate_greedy(requests, allow_partial=True)
    print_allocation_results(result_greedy, "Greedy with Partial Funding")
    
    # Step 3: Demonstrate proportional allocation
    result_proportional = allocator.allocate_proportional(requests, reserve_ratio=0.1)
    print_allocation_results(result_proportional, "Proportional Allocation")
    
    # Step 4: Demonstrate knapsack optimization
    result_knapsack = allocator.allocate_knapsack(requests)
    print_allocation_results(result_knapsack, "Knapsack Optimization")
    
    # Step 5: Compare all strategies
    compare_all_strategies(requests, total_budget)
    
    print("\n[COMPLETE] Analysis complete!\n")


if __name__ == "__main__":
    main()
