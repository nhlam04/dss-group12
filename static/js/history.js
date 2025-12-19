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
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

loadHistory();
