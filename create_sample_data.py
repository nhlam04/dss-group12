

from database import Database
from charity_decision_system import ProgramCategory, UrgencyLevel

db = Database()

print("Creating sample data...")

# Add Charity Agents
print("\nAdding charity agents...")

agents_data = [
    ("Health First Foundation", 0.85, 20, 17),  # 85% success rate
    ("Education for All", 0.90, 15, 12),  # 80% success rate
    ("Clean Water Initiative", 0.75, 12, 9),  # 75% success rate
    ("Food Security Network", 0.95, 25, 24),  # 96% success rate
    ("Disaster Relief Coalition", 0.70, 10, 7),  # 70% success rate
    ("Green Earth Project", 0.65, 8, 5),  # 62.5% success rate
    ("Community Housing Alliance", 0.88, 18, 16),  # 88.9% success rate
]

agent_ids = {}
for name, transparency, total_programs, programs_succeeded in agents_data:
    agent_id = db.add_agent(
        name=name,
        transparency_score=transparency,
        total_programs_completed=total_programs,
        programs_succeeded=programs_succeeded
    )
    agent_ids[name] = agent_id
    success_rate = programs_succeeded / total_programs if total_programs > 0 else 0
    print(f"  Added: {name} (ID: {agent_id}, Success Rate: {success_rate:.1%})")

# Add Grant Requests
print("\nAdding grant requests...")

requests_data = [
    # (agent_name, program_name, amount, overhead, people, duration, category, urgency, sustainability)
    ("Health First Foundation", "Mobile Health Clinics for Rural Areas", 75000, 7500, 2500, 12, "HEALTHCARE", "HIGH", 0.8),
    ("Education for All", "After-School STEM Program", 45000, 4500, 800, 10, "EDUCATION", "MEDIUM", 0.9),
    ("Clean Water Initiative", "Village Well Construction Project", 120000, 12000, 5000, 18, "ENVIRONMENT", "CRITICAL", 0.95),
    ("Food Security Network", "Community Food Bank Expansion", 60000, 3000, 1500, 12, "FOOD_SECURITY", "HIGH", 0.7),
    ("Disaster Relief Coalition", "Emergency Flood Response", 200000, 30000, 10000, 3, "DISASTER_RELIEF", "CRITICAL", 0.3),
    ("Green Earth Project", "Urban Tree Planting Initiative", 35000, 5000, 500, 24, "ENVIRONMENT", "LOW", 0.85),
    ("Community Housing Alliance", "Homeless Shelter Renovation", 150000, 22500, 300, 15, "HOUSING", "HIGH", 0.6),
    ("Health First Foundation", "Maternal Health Education Program", 55000, 8250, 1200, 9, "HEALTHCARE", "MEDIUM", 0.75),
    ("Education for All", "Adult Literacy Classes", 30000, 3000, 600, 12, "EDUCATION", "MEDIUM", 0.8),
    ("Food Security Network", "School Lunch Program", 80000, 8000, 3000, 12, "FOOD_SECURITY", "HIGH", 0.85),
    ("Clean Water Initiative", "Water Filtration System Installation", 95000, 14250, 4000, 14, "ENVIRONMENT", "HIGH", 0.9),
    ("Community Housing Alliance", "Affordable Housing Construction", 250000, 37500, 150, 24, "HOUSING", "MEDIUM", 0.95),
    ("Disaster Relief Coalition", "Earthquake Recovery Fund", 180000, 27000, 8000, 6, "DISASTER_RELIEF", "CRITICAL", 0.4),
    ("Green Earth Project", "Beach Cleanup Campaign", 20000, 2000, 200, 6, "ENVIRONMENT", "LOW", 0.5),
    ("Health First Foundation", "COVID-19 Vaccination Drive", 110000, 16500, 15000, 6, "HEALTHCARE", "CRITICAL", 0.6),
]

for agent_name, program_name, amount, overhead, people, duration, category, urgency, sustainability in requests_data:
    request_id = db.add_request(
        agent_id=agent_ids[agent_name],
        program_name=program_name,
        amount_requested=amount,
        overhead_cost=overhead,
        people_benefitted=people,
        duration_months=duration,
        category=category,
        urgency=urgency,
        sustainability_score=sustainability
    )
    print(f"  Added: {program_name} (ID: {request_id}) - ${amount:,.0f} for {people} people")

# Set Fund Configuration
print("\nConfiguring fund budget...")
db.update_fund_config(
    total_budget=500000,  # $500,000 total budget
    allocated_budget=0,
    min_allocation_percentage=0.5  # Must fund at least 50% or reject
)
print("  Total Budget: $500,000")
print("  Min Allocation: 50%")

# Update TOPSIS criteria weights (optional - using defaults)
print("\nTOPSIS criteria weights (default):")
weights = db.get_criteria_weights()
for criterion, weight in weights.items():
    print(f"  {criterion}: {weight:.1%}")

print("\n" + "="*60)
print("Sample database created successfully!")
print("="*60)
print("\nDatabase Summary:")
print(f"  - {len(agents_data)} Charity Agents")
print(f"  - {len(requests_data)} Grant Requests")
print(f"  - Total Funding Requested: ${sum(r[2] for r in requests_data):,.0f}")
print(f"  - Available Budget: $500,000")
print(f"  - Total People to Benefit: {sum(r[4] for r in requests_data):,}")
print("\nYou can now:")
print("  1. Start the web server: python app.py")
print("  2. Open http://localhost:5000")
print("  3. Navigate to 'Allocate Funds' to run allocation analysis")
print("="*60)
