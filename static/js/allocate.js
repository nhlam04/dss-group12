// Allocation Management

let currentResult = null;

// Preview allocation
async function previewAllocation() {
    const strategy = document.getElementById('strategy').value;
    
    // Show loading spinner
    document.getElementById('loadingMessage').style.display = 'none';
    document.getElementById('loadingSpinner').style.display = 'block';
    document.getElementById('resultsTable').style.display = 'none';
    
    try {
        const response = await fetch('/api/allocate/preview', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({strategy})
        });
        
        if (response.ok) {
            currentResult = await response.json();
            displayResults(currentResult);
        } else {
            const error = await response.json();
            showError(error.error);
            document.getElementById('loadingSpinner').style.display = 'none';
            document.getElementById('loadingMessage').style.display = 'block';
        }
    } catch (error) {
        showError('Failed to preview allocation: ' + error.message);
        document.getElementById('loadingSpinner').style.display = 'none';
        document.getElementById('loadingMessage').style.display = 'block';
    }
}

// Run allocation
document.getElementById('allocationForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!confirm('Are you sure you want to run this allocation? This will update the database.')) return;
    
    const strategy = document.getElementById('strategy').value;
    
    // Show loading spinner
    document.getElementById('loadingMessage').style.display = 'none';
    document.getElementById('loadingSpinner').style.display = 'block';
    document.getElementById('resultsTable').style.display = 'none';
    
    try {
        const response = await fetch('/api/allocate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({strategy})
        });
        
        if (response.ok) {
            currentResult = await response.json();
            displayResults(currentResult);
            showSuccess('Allocation completed successfully!');
        } else {
            const error = await response.json();
            showError(error.error);
            document.getElementById('loadingSpinner').style.display = 'none';
            document.getElementById('loadingMessage').style.display = 'block';
        }
    } catch (error) {
        showError('Failed to run allocation: ' + error.message);
        document.getElementById('loadingSpinner').style.display = 'none';
        document.getElementById('loadingMessage').style.display = 'block';
    }
});

// Display allocation results
function displayResults(result) {
    // Show summary
    document.getElementById('summaryCard').style.display = 'block';
    document.getElementById('sumBudget').textContent = formatCurrency(result.total_budget);
    document.getElementById('sumAllocated').textContent = formatCurrency(result.total_allocated);
    document.getElementById('sumRemaining').textContent = formatCurrency(result.remaining_budget);
    document.getElementById('sumUtilization').textContent = formatPercent(result.utilization_rate / 100);
    document.getElementById('sumFull').textContent = result.num_fully_funded;
    document.getElementById('sumPartial').textContent = result.num_partially_funded;
    document.getElementById('sumRejected').textContent = result.num_rejected;
    document.getElementById('sumPeople').textContent = formatNumber(result.total_people_benefitted);
    document.getElementById('sumEfficiency').textContent = formatPercent(result.average_efficiency_ratio);
    
    // Show decisions table
    document.getElementById('loadingMessage').style.display = 'none';
    document.getElementById('loadingSpinner').style.display = 'none';
    document.getElementById('resultsTable').style.display = 'block';
    
    const tbody = document.getElementById('decisionsTable');
    tbody.innerHTML = '';
    
    result.decisions.forEach(decision => {
        let statusBadge;
        if (decision.is_fully_funded) {
            statusBadge = '<span class="badge bg-success">FULL</span>';
        } else if (decision.is_partially_funded) {
            statusBadge = '<span class="badge bg-warning">PARTIAL</span>';
        } else {
            statusBadge = '<span class="badge bg-danger">REJECTED</span>';
        }
        
        const row = `
            <tr>
                <td>${decision.rank || 0}</td>
                <td>${decision.program_name || 'N/A'}</td>
                <td>${decision.agent_name || 'N/A'}</td>
                <td>${formatCurrency(decision.amount_requested || 0)}</td>
                <td>${formatCurrency(decision.amount_allocated || 0)}</td>
                <td>${formatPercent(decision.allocation_percentage || 0)}</td>
                <td>${(decision.priority_score || 0).toFixed(4)}</td>
                <td>${formatNumber(decision.people_benefitted || 0)}</td>
                <td>${statusBadge}</td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}
