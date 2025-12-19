// Charity Agents Management

let agents = [];

// Load all agents
async function loadAgents() {
    try {
        const response = await fetch('/api/agents');
        agents = await response.json();
        displayAgents();
    } catch (error) {
        showError('Failed to load agents: ' + error.message);
    }
}

// Display agents in table
function displayAgents() {
    const tbody = document.getElementById('agentsTable');
    tbody.innerHTML = '';
    
    agents.forEach(agent => {
        const row = `
            <tr>
                <td>${agent.agent_id}</td>
                <td>${agent.name}</td>
                <td>${formatPercent(agent.success_rate)}</td>
                <td>${formatPercent(agent.transparency_score)}</td>
                <td>${agent.total_programs_completed}</td>
                <td>${agent.programs_succeeded}</td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="deleteAgent('${agent.agent_id}')">
                        <i class="bi bi-trash"></i> Delete
                    </button>
                </td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

// Add new agent
document.getElementById('addAgentForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const totalPrograms = parseInt(document.getElementById('totalPrograms').value);
    const programsSucceeded = parseInt(document.getElementById('programsSucceeded').value);
    
    // Validate programs succeeded doesn't exceed total
    if (programsSucceeded > totalPrograms) {
        showError('Programs succeeded cannot exceed total programs completed');
        return;
    }
    
    const agentData = {
        name: document.getElementById('agentName').value,
        transparency_score: parseFloat(document.getElementById('transparencyScore').value),
        total_programs_completed: totalPrograms,
        programs_succeeded: programsSucceeded
    };
    
    try {
        const response = await fetch('/api/agents', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(agentData)
        });
        
        if (response.ok) {
            showSuccess('Agent added successfully');
            bootstrap.Modal.getInstance(document.getElementById('addAgentModal')).hide();
            document.getElementById('addAgentForm').reset();
            loadAgents();
        } else {
            const error = await response.json();
            showError(error.error);
        }
    } catch (error) {
        showError('Failed to add agent: ' + error.message);
    }
});

// Delete agent
async function deleteAgent(agentId) {
    if (!confirm('Are you sure you want to delete this agent?')) return;
    
    try {
        const response = await fetch(`/api/agents/${agentId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showSuccess('Agent deleted successfully');
            loadAgents();
        } else {
            const error = await response.json();
            showError(error.error);
        }
    } catch (error) {
        showError('Failed to delete agent: ' + error.message);
    }
}

// Load agents on page load
loadAgents();
