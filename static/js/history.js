// Allocation History

async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        const history = await response.json();
        displayHistory(history);
    } catch (error) {
        showError('Failed to load history: ' + error.message);
    }
}

function displayHistory(history) {
    const tbody = document.getElementById('historyTable');
    tbody.innerHTML = '';
    
    history.forEach(allocation => {
        const date = new Date(allocation.allocation_date);
        const utilization = (allocation.total_allocated / allocation.total_budget * 100).toFixed(1);
        
        const row = `
            <tr>
                <td>${date.toLocaleString()}</td>
                <td><span class="badge bg-primary">${allocation.strategy_name}</span></td>
                <td>${formatCurrency(allocation.total_budget)}</td>
                <td>${formatCurrency(allocation.total_allocated)}</td>
                <td>${utilization}%</td>
                <td>${allocation.num_fully_funded}</td>
                <td>${allocation.num_partially_funded}</td>
                <td>${allocation.num_rejected}</td>
                <td>${formatNumber(allocation.total_people_benefitted)}</td>
                <td>
                    <button class="btn btn-sm btn-info" onclick="viewAllocationDetails(${allocation.allocation_id})">
                        <i class="bi bi-eye"></i> View Details
                    </button>
                </td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

async function viewAllocationDetails(allocationId) {
    try {
        const response = await fetch(`/api/history/${allocationId}`);
        const details = await response.json();
        
        // Update summary cards
        document.getElementById('detailBudget').textContent = formatCurrency(details.total_budget);
        document.getElementById('detailAllocated').textContent = formatCurrency(details.total_allocated);
        document.getElementById('detailRemaining').textContent = formatCurrency(details.remaining_budget);
        const utilization = (details.total_allocated / details.total_budget * 100).toFixed(1);
        document.getElementById('detailUtilization').textContent = utilization + '%';
        
        // Display decisions
        const tbody = document.getElementById('detailDecisionsTable');
        tbody.innerHTML = '';
        
        details.decisions.forEach(decision => {
            let statusBadge;
            if (decision.allocation_percentage >= 0.99) {
                statusBadge = '<span class="badge bg-success">FULL</span>';
            } else if (decision.allocation_percentage > 0) {
                statusBadge = '<span class="badge bg-warning">PARTIAL</span>';
            } else {
                statusBadge = '<span class="badge bg-danger">REJECTED</span>';
            }
            
            const row = `
                <tr>
                    <td>${decision.rank}</td>
                    <td>${decision.program_name}</td>
                    <td>${decision.agent_name}</td>
                    <td>${formatCurrency(decision.amount_requested)}</td>
                    <td>${formatCurrency(decision.amount_allocated)}</td>
                    <td>${formatPercent(decision.allocation_percentage)}</td>
                    <td>${decision.priority_score.toFixed(4)}</td>
                    <td>${formatNumber(decision.people_benefitted)}</td>
                    <td>${statusBadge}</td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('allocationDetailsModal'));
        modal.show();
    } catch (error) {
        showError('Failed to load allocation details: ' + error.message);
    }
}

loadHistory();
