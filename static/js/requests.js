// Grant Requests Management

let requests = [];
let agents = [];
let currentFilter = null;

// Load all requests
async function loadRequests(status = undefined) {
    if (status !== undefined) {
        currentFilter = status;
    }

    try {
        const url = currentFilter ? `/api/requests?status=${currentFilter}` : '/api/requests';
        const response = await fetch(url);

        if (!response.ok) {
            const error = await response.json();
            showError(error.error || 'Failed to load requests');
            return;
        }

        requests = await response.json();

        // Ensure requests is an array
        if (!Array.isArray(requests)) {
            console.error('Invalid response:', requests);
            showError('Invalid response from server');
            requests = [];
            return;
        }

        displayRequests();
    } catch (error) {
        showError('Failed to load requests: ' + error.message);
        requests = [];
    }
}

// Load agents for dropdown
async function loadAgents() {
    try {
        const response = await fetch('/api/agents');
        agents = await response.json();

        const select = document.getElementById('agentSelect');
        select.innerHTML = '<option value="">Select an agent...</option>';
        agents.forEach(agent => {
            select.innerHTML += `<option value="${agent.agent_id}">${agent.name}</option>`;
        });
    } catch (error) {
        showError('Failed to load agents: ' + error.message);
    }
}

// Load enums
async function loadEnums() {
    try {
        const [categoriesRes, urgencyRes] = await Promise.all([
            fetch('/api/enums/categories'),
            fetch('/api/enums/urgency-levels')
        ]);

        const categories = await categoriesRes.json();
        const urgencyLevels = await urgencyRes.json();

        const categorySelect = document.getElementById('category');
        categories.forEach(cat => {
            categorySelect.innerHTML += `<option value="${cat}">${cat}</option>`;
        });

        const urgencySelect = document.getElementById('urgency');
        urgencyLevels.forEach(level => {
            urgencySelect.innerHTML += `<option value="${level}">${level}</option>`;
        });
    } catch (error) {
        showError('Failed to load options: ' + error.message);
    }
}

// Display requests in table
function displayRequests() {
    const tbody = document.getElementById('requestsTable');
    tbody.innerHTML = '';

    requests.forEach(req => {
        let statusBadge = '';
        if (req.status === 'pending') {
            statusBadge = '<span class="badge bg-warning">Pending</span>';
        } else if (req.status === 'funded') {
            if (req.succeeded === true) {
                statusBadge = '<span class="badge bg-success">Funded</span> <span class="badge bg-success">Succeeded</span>';
            } else if (req.succeeded === false) {
                statusBadge = '<span class="badge bg-success">Funded</span> <span class="badge bg-danger">Failed</span>';
            } else {
                statusBadge = '<span class="badge bg-success">Funded</span>';
            }
        } else if (req.status === 'rejected') {
            if (req.succeeded === true) {
                statusBadge = '<span class="badge bg-danger">Rejected</span> <span class="badge bg-success">Succeeded</span>';
            } else if (req.succeeded === false) {
                statusBadge = '<span class="badge bg-danger">Rejected</span> <span class="badge bg-danger">Failed</span>';
            } else {
                statusBadge = '<span class="badge bg-danger">Rejected</span>';
            }
        } else if (req.status === 'completed') {
            // Legacy support for old data
            statusBadge = req.succeeded ?
                '<span class="badge bg-success">Succeeded</span>' :
                '<span class="badge bg-danger">Failed</span>';
        }

        let actionButtons = '';
        if (req.status === 'funded' || req.status === 'rejected') {
            // Only show succeed/fail buttons if not yet marked (succeeded is null or undefined)
            if (req.succeeded === null || req.succeeded === undefined) {
                actionButtons = `
                    <button class="btn btn-sm btn-success" onclick="markCompleted(${req.request_id}, true)" title="Mark as Succeeded">
                        <i class="bi bi-check-circle"></i>
                    </button>
                    <button class="btn btn-sm btn-warning" onclick="markCompleted(${req.request_id}, false)" title="Mark as Failed">
                        <i class="bi bi-x-circle"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteRequest(${req.request_id})">
                        <i class="bi bi-trash"></i>
                    </button>
                `;
            } else {
                // Already marked, only show delete
                actionButtons = `
                    <button class="btn btn-sm btn-danger" onclick="deleteRequest(${req.request_id})">
                        <i class="bi bi-trash"></i>
                    </button>
                `;
            }
        } else if (req.status === 'pending') {
            // Pending requests can only be deleted
            actionButtons = `
                <button class="btn btn-sm btn-danger" onclick="deleteRequest(${req.request_id})">
                    <i class="bi bi-trash"></i>
                </button>
            `;
        } else {
            // For any other status (like 'completed'), only show delete
            actionButtons = `
                <button class="btn btn-sm btn-danger" onclick="deleteRequest(${req.request_id})">
                    <i class="bi bi-trash"></i>
                </button>
            `;
        }

        const row = `
            <tr>
                <td>${req.request_id}</td>
                <td>${req.program_name}</td>
                <td>${req.agent_name}</td>
                <td>${formatCurrency(req.amount_requested)}</td>
                <td>${formatNumber(req.people_benefitted)}</td>
                <td>${formatPercent(req.efficiency_ratio)}</td>
                <td><span class="badge bg-info">${req.category}</span></td>
                <td><span class="badge bg-warning">${req.urgency}</span></td>
                <td>${statusBadge}</td>
                <td>${actionButtons}</td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

// Filter requests
function filterRequests(status) {
    // Update button states
    document.querySelectorAll('.btn-group button').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    loadRequests(status === 'all' ? null : status);
}

// Add new request
document.getElementById('addRequestForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const requestData = {
        agent_id: document.getElementById('agentSelect').value,
        program_name: document.getElementById('programName').value,
        amount_requested: parseFloat(document.getElementById('amountRequested').value),
        overhead_cost: parseFloat(document.getElementById('overheadCost').value),
        people_benefitted: parseInt(document.getElementById('peopleBenefitted').value),
        duration_months: parseInt(document.getElementById('durationMonths').value),
        category: document.getElementById('category').value,
        urgency: document.getElementById('urgency').value,
        sustainability_score: parseFloat(document.getElementById('sustainabilityScore').value)
    };

    try {
        const response = await fetch('/api/requests', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });

        if (response.ok) {
            showSuccess('Request added successfully');
            bootstrap.Modal.getInstance(document.getElementById('addRequestModal')).hide();
            document.getElementById('addRequestForm').reset();
            loadRequests(currentFilter);
        } else {
            const error = await response.json();
            showError(error.error);
        }
    } catch (error) {
        showError('Failed to add request: ' + error.message);
    }
});

// Mark request as completed
async function markCompleted(requestId, succeeded) {
    const status = succeeded ? 'succeeded' : 'failed';

    try {
        const response = await fetch(`/api/requests/${requestId}/complete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ succeeded })
        });

        if (response.ok) {
            showSuccess(`Request marked as ${status}. Agent statistics updated.`);
            loadRequests(currentFilter);
        } else {
            const error = await response.json();
            showError(error.error);
        }
    } catch (error) {
        showError('Failed to update request: ' + error.message);
    }
}

// Delete request
async function deleteRequest(requestId) {
    if (!confirm('Are you sure you want to delete this request?')) return;

    try {
        const response = await fetch(`/api/requests/${requestId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showSuccess('Request deleted successfully');
            loadRequests(currentFilter);
        } else {
            const error = await response.json();
            showError(error.error);
        }
    } catch (error) {
        showError('Failed to delete request: ' + error.message);
    }
}

// Initialize
loadRequests();
loadAgents();
loadEnums();
