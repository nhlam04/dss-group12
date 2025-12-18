"""
Interactive Command-Line Interface for Charity Fund Decision Support
Allows users to input their own data and run allocation strategies
"""

import json
from typing import List
from charity_decision_system import (
    CharityAgent, GrantRequest, ProgramCategory, UrgencyLevel,
    AllocationDecision
)
from fund_allocator import FundAllocator
from topsis_analyzer import TOPSISAnalyzer


def print_header():
    """Print application header"""
    print("\n" + "=" * 80)
    print(" " * 20 + "CHARITY FUND DECISION SUPPORT SYSTEM")
    print("=" * 80)


def print_menu():
    """Display main menu"""
    print("\nMAIN MENU:")
    print("1. Load sample data")
    print("2. Input custom grant requests")
    print("3. Run allocation analysis")
    print("4. Compare allocation strategies")
    print("5. Export results to JSON")
    print("6. View current requests")
    print("7. Exit")
    print("-" * 80)


def get_urgency_level():
    """Interactive urgency level selection"""
    print("\nUrgency Levels:")
    print("1. CRITICAL (Immediate need)")
    print("2. HIGH (Urgent but not immediate)")
    print("3. MEDIUM (Standard timeline)")
    print("4. LOW (Can be delayed)")
    print("5. FLEXIBLE (No time constraints)")
    
    choice = input("Select urgency level (1-5): ").strip()
    urgency_map = {
        '1': UrgencyLevel.CRITICAL,
        '2': UrgencyLevel.HIGH,
        '3': UrgencyLevel.MEDIUM,
        '4': UrgencyLevel.LOW,
        '5': UrgencyLevel.FLEXIBLE
    }
    return urgency_map.get(choice, UrgencyLevel.MEDIUM)


def get_program_category():
    """Interactive program category selection"""
    print("\nProgram Categories:")
    print("1. Healthcare")
    print("2. Education")
    print("3. Food Security")
    print("4. Disaster Relief")
    print("5. Housing")
    print("6. Environment")
    print("7. Other")
    
    choice = input("Select category (1-7): ").strip()
    category_map = {
        '1': ProgramCategory.HEALTHCARE,
        '2': ProgramCategory.EDUCATION,
        '3': ProgramCategory.FOOD_SECURITY,
        '4': ProgramCategory.DISASTER_RELIEF,
        '5': ProgramCategory.HOUSING,
        '6': ProgramCategory.ENVIRONMENT,
        '7': ProgramCategory.OTHER
    }
    return category_map.get(choice, ProgramCategory.OTHER)


def input_agent():
    """Interactive agent input"""
    print("\n" + "-" * 80)
    print("CHARITY AGENT INFORMATION")
    print("-" * 80)
    
    agent_id = input("Agent ID: ").strip()
    name = input("Organization Name: ").strip()
    
    while True:
        try:
            success_rate = float(input("Historical Success Rate (0-1, e.g., 0.85): ").strip())
            if 0 <= success_rate <= 1:
                break
            print("Error: Must be between 0 and 1")
        except ValueError:
            print("Error: Please enter a valid number")
    
    while True:
        try:
            transparency = float(input("Transparency Score (0-1, e.g., 0.90): ").strip())
            if 0 <= transparency <= 1:
                break
            print("Error: Must be between 0 and 1")
        except ValueError:
            print("Error: Please enter a valid number")
    
    while True:
        try:
            total_programs = int(input("Total Programs Completed: ").strip())
            if total_programs >= 0:
                break
            print("Error: Must be non-negative")
        except ValueError:
            print("Error: Please enter a valid integer")
    
    while True:
        try:
            succeeded = int(input("Programs Succeeded: ").strip())
            if 0 <= succeeded <= total_programs:
                break
            print(f"Error: Must be between 0 and {total_programs}")
        except ValueError:
            print("Error: Please enter a valid integer")
    
    return CharityAgent(
        agent_id=agent_id,
        name=name,
        success_rate=success_rate,
        transparency_score=transparency,
        total_programs_completed=total_programs,
        programs_succeeded=succeeded
    )


def input_grant_request(agent: CharityAgent):
    """Interactive grant request input"""
    print("\n" + "-" * 80)
    print("GRANT REQUEST INFORMATION")
    print("-" * 80)
    
    request_id = input("Request ID: ").strip()
    program_name = input("Program Name: ").strip()
    
    while True:
        try:
            amount = float(input("Amount Requested ($): ").strip())
            if amount > 0:
                break
            print("Error: Must be positive")
        except ValueError:
            print("Error: Please enter a valid number")
    
    while True:
        try:
            overhead = float(input("Overhead Cost ($): ").strip())
            if 0 <= overhead < amount:
                break
            print(f"Error: Must be between 0 and {amount}")
        except ValueError:
            print("Error: Please enter a valid number")
    
    while True:
        try:
            people = int(input("People Benefitted: ").strip())
            if people > 0:
                break
            print("Error: Must be positive")
        except ValueError:
            print("Error: Please enter a valid integer")
    
    while True:
        try:
            duration = int(input("Duration (months): ").strip())
            if duration > 0:
                break
            print("Error: Must be positive")
        except ValueError:
            print("Error: Please enter a valid integer")
    
    category = get_program_category()
    urgency = get_urgency_level()
    
    location = input("Geographic Location: ").strip()
    
    while True:
        try:
            sustainability = float(input("Sustainability Score (0-1, e.g., 0.75): ").strip())
            if 0 <= sustainability <= 1:
                break
            print("Error: Must be between 0 and 1")
        except ValueError:
            print("Error: Please enter a valid number")
    
    return GrantRequest(
        request_id=request_id,
        agent=agent,
        program_name=program_name,
        amount_requested=amount,
        overhead_cost=overhead,
        people_benefitted=people,
        duration_months=duration,
        category=category,
        urgency=urgency,
        geographic_location=location,
        sustainability_score=sustainability
    )


def view_requests(requests: List[GrantRequest]):
    """Display current grant requests"""
    if not requests:
        print("\nNo grant requests loaded.")
        return
    
    print("\n" + "=" * 80)
    print("CURRENT GRANT REQUESTS")
    print("=" * 80)
    
    total_requested = sum(r.amount_requested for r in requests)
    
    for i, req in enumerate(requests, 1):
        print(f"\n{i}. {req.program_name}")
        print(f"   Agent: {req.agent.name}")
        print(f"   Requested: ${req.amount_requested:,.0f}")
        print(f"   People: {req.people_benefitted:,}")
        print(f"   Category: {req.category.value}")
        print(f"   Urgency: {req.urgency.name}")
    
    print(f"\nTotal Requested: ${total_requested:,.0f}")
    print("=" * 80)


def run_allocation_analysis(requests: List[GrantRequest]):
    """Run allocation analysis with user-specified budget"""
    if not requests:
        print("\nError: No grant requests loaded. Please load sample data or input custom requests first.")
        return None
    
    print("\n" + "-" * 80)
    print("ALLOCATION ANALYSIS")
    print("-" * 80)
    
    while True:
        try:
            budget = float(input("\nTotal Budget Available ($): ").strip())
            if budget > 0:
                break
            print("Error: Budget must be positive")
        except ValueError:
            print("Error: Please enter a valid number")
    
    while True:
        try:
            min_pct = float(input("Minimum Allocation Percentage (0-1, e.g., 0.5): ").strip())
            if 0 <= min_pct <= 1:
                break
            print("Error: Must be between 0 and 1")
        except ValueError:
            print("Error: Please enter a valid number")
    
    print("\nAllocation Strategies:")
    print("1. Greedy (Full Funding Only)")
    print("2. Greedy (Allow Partial Funding)")
    print("3. Proportional Allocation")
    print("4. Knapsack Optimization")
    
    strategy = input("\nSelect strategy (1-4): ").strip()
    
    allocator = FundAllocator(total_budget=budget, min_allocation_percentage=min_pct)
    
    if strategy == '1':
        result = allocator.allocate_greedy(requests, allow_partial=False)
        strategy_name = "Greedy (Full Funding)"
    elif strategy == '2':
        result = allocator.allocate_greedy(requests, allow_partial=True)
        strategy_name = "Greedy (Partial Allowed)"
    elif strategy == '3':
        result = allocator.allocate_proportional(requests)
        strategy_name = "Proportional"
    elif strategy == '4':
        result = allocator.allocate_knapsack(requests)
        strategy_name = "Knapsack"
    else:
        print("Invalid choice. Using Greedy (Partial Allowed).")
        result = allocator.allocate_greedy(requests, allow_partial=True)
        strategy_name = "Greedy (Partial Allowed)"
    
    print("\n" + "=" * 80)
    print(f"RESULTS - {strategy_name}")
    print("=" * 80)
    print(result.summary())
    
    print("\nDETAILED DECISIONS:")
    print("-" * 80)
    
    for decision in sorted(result.decisions, key=lambda d: d.rank):
        symbol = "[FULL]" if decision.is_fully_funded() else "[PART]" if decision.is_partially_funded() else "[REJ]"
        print(f"\n{symbol} Rank #{decision.rank}: {decision.request.program_name}")
        print(f"   Allocated: ${decision.amount_allocated:,.0f} ({decision.allocation_percentage:.0%})")
        print(f"   Rationale: {decision.rationale}")
    
    print("\n" + "=" * 80)
    
    return result


def compare_strategies(requests: List[GrantRequest]):
    """Compare all allocation strategies"""
    if not requests:
        print("\nError: No grant requests loaded.")
        return
    
    while True:
        try:
            budget = float(input("\nTotal Budget Available ($): ").strip())
            if budget > 0:
                break
            print("Error: Budget must be positive")
        except ValueError:
            print("Error: Please enter a valid number")
    
    allocator = FundAllocator(total_budget=budget)
    results = allocator.compare_strategies(requests)
    
    print("\n" + "=" * 80)
    print("STRATEGY COMPARISON")
    print("=" * 80)
    
    for name, result in results.items():
        print(f"\n{name.upper()}:")
        print(f"  Allocated: ${result.total_allocated:,.0f} ({result.utilization_rate():.1f}%)")
        print(f"  Fully Funded: {result.num_fully_funded}")
        print(f"  Partially Funded: {result.num_partially_funded}")
        print(f"  Rejected: {result.num_rejected}")
        print(f"  People Benefitted: {result.total_people_benefitted:,}")
        print(f"  Avg Efficiency: {result.average_efficiency_ratio:.1%}")
    
    print("\n" + "=" * 80)


def export_results(result, filename: str = "allocation_results.json"):
    """Export results to JSON file"""
    if result is None:
        print("\nError: No results to export. Run an allocation analysis first.")
        return
    
    output = {
        'budget': {
            'total': result.total_budget,
            'allocated': result.total_allocated,
            'remaining': result.remaining_budget,
            'utilization_rate': result.utilization_rate()
        },
        'summary': {
            'fully_funded': result.num_fully_funded,
            'partially_funded': result.num_partially_funded,
            'rejected': result.num_rejected,
            'people_benefitted': result.total_people_benefitted,
            'average_efficiency': result.average_efficiency_ratio
        },
        'decisions': []
    }
    
    for decision in result.decisions:
        output['decisions'].append({
            'rank': decision.rank,
            'program_name': decision.request.program_name,
            'agent': decision.request.agent.name,
            'requested': decision.request.amount_requested,
            'allocated': decision.amount_allocated,
            'allocation_percentage': decision.allocation_percentage,
            'priority_score': decision.priority_score,
            'people_benefitted': int(decision.request.people_benefitted * decision.allocation_percentage),
            'rationale': decision.rationale
        })
    
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n[OK] Results exported to {filename}")


def main():
    """Main application loop"""
    print_header()
    
    requests = []
    last_result = None
    
    while True:
        print_menu()
        choice = input("Enter your choice (1-7): ").strip()
        
        if choice == '1':
            # Load sample data
            from example_usage import create_sample_requests
            requests = create_sample_requests()
            print(f"\n[OK] Loaded {len(requests)} sample grant requests.")
        
        elif choice == '2':
            # Input custom data
            print("\nHow many grant requests do you want to input?")
            try:
                num_requests = int(input("Number of requests: ").strip())
            except ValueError:
                print("Error: Invalid number")
                continue
            
            requests = []
            agents = {}
            
            for i in range(num_requests):
                print(f"\n--- Request {i+1}/{num_requests} ---")
                
                print("\nDo you want to:")
                print("1. Create a new agent")
                print("2. Use an existing agent")
                
                agent_choice = input("Choice (1-2): ").strip()
                
                if agent_choice == '2' and agents:
                    print("\nExisting agents:")
                    for idx, (aid, agent) in enumerate(agents.items(), 1):
                        print(f"{idx}. {agent.name} ({aid})")
                    
                    try:
                        agent_idx = int(input("Select agent (number): ").strip()) - 1
                        agent = list(agents.values())[agent_idx]
                    except (ValueError, IndexError):
                        print("Invalid selection. Creating new agent.")
                        agent = input_agent()
                        agents[agent.agent_id] = agent
                else:
                    agent = input_agent()
                    agents[agent.agent_id] = agent
                
                request = input_grant_request(agent)
                requests.append(request)
            
            print(f"\n[OK] Added {len(requests)} grant requests.")
        
        elif choice == '3':
            # Run allocation analysis
            last_result = run_allocation_analysis(requests)
        
        elif choice == '4':
            # Compare strategies
            compare_strategies(requests)
        
        elif choice == '5':
            # Export results
            filename = input("\nOutput filename (default: allocation_results.json): ").strip()
            if not filename:
                filename = "allocation_results.json"
            export_results(last_result, filename)
        
        elif choice == '6':
            # View requests
            view_requests(requests)
        
        elif choice == '7':
            # Exit
            print("\nThank you for using the Charity Fund Decision Support System!")
            print("=" * 80 + "\n")
            break
        
        else:
            print("\nInvalid choice. Please select 1-7.")


if __name__ == "__main__":
    main()
