"""
Flask Web Application - Backend API
RESTful API for charity fund decision support system
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime

from database import Database
from charity_decision_system import (
    CharityAgent, GrantRequest, ProgramCategory, UrgencyLevel
)
from fund_allocator import FundAllocator
from topsis_analyzer import TOPSISAnalyzer

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
CORS(app)

# Initialize database
db = Database()

# ===== PAGES =====

@app.route('/')
def index():
    """Dashboard page"""
    return render_template('index.html')

@app.route('/agents')
def agents_page():
    """Charity agents management page"""
    return render_template('agents.html')

@app.route('/requests')
def requests_page():
    """Grant requests management page"""
    return render_template('requests.html')

@app.route('/allocate')
def allocate_page():
    """Allocation analysis page"""
    return render_template('allocate.html')

@app.route('/history')
def history_page():
    """Allocation history page"""
    return render_template('history.html')

@app.route('/settings')
def settings_page():
    """Settings page"""
    return render_template('settings.html')

# ===== API ENDPOINTS =====

# --- Stats ---
@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    try:
        stats = db.get_stats()
        fund_config = db.get_fund_config()
        stats.update(fund_config)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Charity Agents ---
@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get all charity agents"""
    try:
        agents = db.get_all_agents()
        return jsonify([{
            'agent_id': a.agent_id,
            'name': a.name,
            'success_rate': a.success_rate,  # Calculated property
            'transparency_score': a.transparency_score,
            'total_programs_completed': a.total_programs_completed,
            'programs_succeeded': a.programs_succeeded
        } for a in agents])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/agents/<int:agent_id>', methods=['GET'])
def get_agent(agent_id):
    """Get a specific agent"""
    try:
        agent = db.get_agent(agent_id)
        if agent:
            return jsonify({
                'agent_id': agent.agent_id,
                'name': agent.name,
                'success_rate': agent.success_rate,
                'transparency_score': agent.transparency_score,
                'total_programs_completed': agent.total_programs_completed,
                'programs_succeeded': agent.programs_succeeded
            })
        return jsonify({'error': 'Agent not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/agents', methods=['POST'])
def create_agent():
    """Create a new charity agent"""
    try:
        data = request.json
        agent_id = db.add_agent(
            name=data['name'],
            transparency_score=float(data['transparency_score']),
            total_programs_completed=int(data.get('total_programs_completed', 0)),
            programs_succeeded=int(data.get('programs_succeeded', 0))
        )
        
        return jsonify({
            'message': 'Agent created successfully',
            'agent_id': agent_id
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/agents/<int:agent_id>', methods=['PUT'])
def update_agent(agent_id):
    """Update a charity agent"""
    try:
        data = request.json
        
        if db.update_agent(
            agent_id=agent_id,
            name=data['name'],
            transparency_score=float(data['transparency_score']),
            total_programs_completed=int(data['total_programs_completed']),
            programs_succeeded=int(data['programs_succeeded'])
        ):
            return jsonify({'message': 'Agent updated successfully'})
        else:
            return jsonify({'error': 'Agent not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/agents/<int:agent_id>', methods=['DELETE'])
def delete_agent(agent_id):
    """Delete a charity agent"""
    try:
        if db.delete_agent(agent_id):
            return jsonify({'message': 'Agent deleted successfully'})
        else:
            return jsonify({'error': 'Agent not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Grant Requests ---
@app.route('/api/requests', methods=['GET'])
def get_requests():
    """Get all grant requests"""
    try:
        status = request.args.get('status')
        requests_list = db.get_all_requests(status)
        
        return jsonify([{
            'request_id': r.request_id,
            'agent_id': r.agent.agent_id,
            'agent_name': r.agent.name,
            'program_name': r.program_name,
            'amount_requested': r.amount_requested,
            'overhead_cost': r.overhead_cost,
            'net_charity_amount': r.net_charity_amount,
            'people_benefitted': r.people_benefitted,
            'duration_months': r.duration_months,
            'category': r.category.name,
            'urgency': r.urgency.name,
            'sustainability_score': r.sustainability_score,
            'status': r.status,
            'succeeded': bool(r.succeeded),
            'efficiency_ratio': r.efficiency_ratio(),
            'cost_per_person': r.cost_per_person()
        } for r in requests_list])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/requests', methods=['POST'])
def create_request():
    """Create a new grant request"""
    try:
        data = request.json
        
        # Validate agent exists
        agent = db.get_agent(int(data['agent_id']))
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
        
        request_id = db.add_request(
            agent_id=int(data['agent_id']),
            program_name=data['program_name'],
            amount_requested=float(data['amount_requested']),
            overhead_cost=float(data['overhead_cost']),
            people_benefitted=int(data['people_benefitted']),
            duration_months=int(data['duration_months']),
            category=data['category'],
            urgency=data['urgency'],
            sustainability_score=float(data['sustainability_score'])
        )
        
        return jsonify({
            'message': 'Request created successfully',
            'request_id': request_id
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/requests/<int:request_id>', methods=['DELETE'])
def delete_request(request_id):
    """Delete a grant request"""
    try:
        if db.delete_request(request_id):
            return jsonify({'message': 'Request deleted successfully'})
        else:
            return jsonify({'error': 'Request not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/requests/<int:request_id>/complete', methods=['POST'])
def mark_request_completed(request_id):
    """Mark a request as completed (succeeded or failed)"""
    try:
        data = request.json
        succeeded = data.get('succeeded', False)
        
        if db.mark_request_completed(request_id, succeeded):
            status = 'succeeded' if succeeded else 'failed'
            return jsonify({
                'message': f'Request marked as completed ({status})',
                'request_id': request_id,
                'succeeded': succeeded
            })
        else:
            return jsonify({'error': 'Request not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Fund Configuration ---
@app.route('/api/fund-config', methods=['GET'])
def get_fund_config():
    """Get fund configuration"""
    try:
        config = db.get_fund_config()
        return jsonify(config)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fund-config', methods=['PUT'])
def update_fund_config():
    """Update fund configuration"""
    try:
        data = request.json
        db.update_fund_config(
            total_budget=data.get('total_budget'),
            allocated_budget=data.get('allocated_budget'),
            min_allocation_percentage=data.get('min_allocation_percentage')
        )
        return jsonify({'message': 'Fund configuration updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# --- Allocation ---
@app.route('/api/allocate', methods=['POST'])
def run_allocation():
    """Run allocation analysis"""
    try:
        data = request.json
        strategy = data.get('strategy', 'greedy_partial')
        
        # Get pending requests
        requests = db.get_all_requests('pending')
        
        if not requests:
            return jsonify({'error': 'No pending requests to allocate'}), 400
        
        # Get fund configuration
        config = db.get_fund_config()
        budget = config['total_budget'] - config['allocated_budget']
        
        if budget <= 0:
            return jsonify({'error': 'No budget remaining'}), 400
        
        # Get criteria weights
        weights = db.get_criteria_weights()
        
        # Create allocator
        allocator = FundAllocator(
            total_budget=budget,
            min_allocation_percentage=config['min_allocation_percentage']
        )
        
        # Set custom weights if provided
        if weights:
            allocator.analyzer.weights = weights
        
        # Run allocation based on strategy
        if strategy == 'greedy_full':
            result = allocator.allocate_greedy(requests, allow_partial=False)
        elif strategy == 'greedy_partial':
            result = allocator.allocate_greedy(requests, allow_partial=True)
        elif strategy == 'proportional':
            result = allocator.allocate_proportional(requests)
        elif strategy == 'knapsack':
            result = allocator.allocate_knapsack(requests)
        else:
            return jsonify({'error': 'Invalid strategy'}), 400
        
        # Save allocation to database
        allocation_id = db.save_allocation(result, strategy)
        
        # Update allocated budget
        new_allocated = config['allocated_budget'] + result.total_allocated
        db.update_fund_config(allocated_budget=new_allocated)
        
        # Return result
        return jsonify({
            'allocation_id': allocation_id,
            'total_budget': result.total_budget,
            'total_allocated': result.total_allocated,
            'remaining_budget': result.remaining_budget,
            'num_fully_funded': result.num_fully_funded,
            'num_partially_funded': result.num_partially_funded,
            'num_rejected': result.num_rejected,
            'total_people_benefitted': result.total_people_benefitted,
            'average_efficiency_ratio': result.average_efficiency_ratio,
            'utilization_rate': result.utilization_rate(),
            'decisions': [{
                'request_id': d.request.request_id,
                'program_name': d.request.program_name,
                'agent_name': d.request.agent.name,
                'amount_requested': d.request.amount_requested,
                'amount_allocated': d.amount_allocated,
                'allocation_percentage': d.allocation_percentage,
                'priority_score': d.priority_score,
                'rank': d.rank,
                'rationale': d.rationale,
                'people_benefitted': int(d.request.people_benefitted * d.allocation_percentage),
                'is_fully_funded': bool(d.is_fully_funded()),
                'is_partially_funded': bool(d.is_partially_funded())
            } for d in result.decisions]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/allocate/preview', methods=['POST'])
def preview_allocation():
    """Preview allocation without saving"""
    try:
        data = request.json
        strategy = data.get('strategy', 'greedy_partial')
        
        requests = db.get_all_requests('pending')
        if not requests:
            return jsonify({'error': 'No pending requests'}), 400
        
        config = db.get_fund_config()
        budget = config['total_budget'] - config['allocated_budget']
        
        if budget <= 0:
            return jsonify({'error': 'No budget remaining'}), 400
        
        weights = db.get_criteria_weights()
        allocator = FundAllocator(
            total_budget=budget,
            min_allocation_percentage=config['min_allocation_percentage']
        )
        
        if weights:
            allocator.analyzer.weights = weights
        
        # Run allocation
        if strategy == 'greedy_full':
            result = allocator.allocate_greedy(requests, allow_partial=False)
        elif strategy == 'greedy_partial':
            result = allocator.allocate_greedy(requests, allow_partial=True)
        elif strategy == 'proportional':
            result = allocator.allocate_proportional(requests)
        elif strategy == 'knapsack':
            result = allocator.allocate_knapsack(requests)
        else:
            return jsonify({'error': 'Invalid strategy'}), 400
        
        return jsonify({
            'total_budget': result.total_budget,
            'total_allocated': result.total_allocated,
            'remaining_budget': result.remaining_budget,
            'num_fully_funded': result.num_fully_funded,
            'num_partially_funded': result.num_partially_funded,
            'num_rejected': result.num_rejected,
            'total_people_benefitted': result.total_people_benefitted,
            'average_efficiency_ratio': result.average_efficiency_ratio,
            'utilization_rate': result.utilization_rate(),
            'decisions': [{
                'request_id': d.request.request_id,
                'program_name': d.request.program_name,
                'agent_name': d.request.agent.name,
                'amount_requested': d.request.amount_requested,
                'amount_allocated': d.amount_allocated,
                'allocation_percentage': d.allocation_percentage,
                'priority_score': d.priority_score,
                'rank': d.rank,
                'rationale': d.rationale,
                'people_benefitted': int(d.request.people_benefitted * d.allocation_percentage),
                'is_fully_funded': bool(d.is_fully_funded()),
                'is_partially_funded': bool(d.is_partially_funded())
            } for d in result.decisions]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Allocation History ---
@app.route('/api/history', methods=['GET'])
def get_history():
    """Get allocation history"""
    try:
        limit = request.args.get('limit', 10, type=int)
        history = db.get_allocation_history(limit)
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Criteria Weights ---
@app.route('/api/criteria-weights', methods=['GET'])
def get_weights():
    """Get criteria weights"""
    try:
        weights = db.get_criteria_weights()
        return jsonify(weights)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/criteria-weights', methods=['PUT'])
def update_weights():
    """Update criteria weights"""
    try:
        weights = request.json
        
        # Validate weights sum to 1
        total = sum(weights.values())
        if not (0.99 <= total <= 1.01):
            return jsonify({'error': f'Weights must sum to 1, got {total}'}), 400
        
        if db.update_criteria_weights(weights):
            return jsonify({'message': 'Weights updated successfully'})
        else:
            return jsonify({'error': 'Failed to update weights'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# --- Enums ---
@app.route('/api/enums/categories', methods=['GET'])
def get_categories():
    """Get program categories"""
    return jsonify([cat.name for cat in ProgramCategory])

@app.route('/api/enums/urgency-levels', methods=['GET'])
def get_urgency_levels():
    """Get urgency levels"""
    return jsonify([level.name for level in UrgencyLevel])


if __name__ == '__main__':
    # Create directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    print("=" * 80)
    print("CHARITY FUND DECISION SUPPORT SYSTEM - WEB APPLICATION")
    print("=" * 80)
    print("\nServer starting...")
    print("Access the application at: http://localhost:5000")
    print("\nPress CTRL+C to stop the server")
    print("=" * 80)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
