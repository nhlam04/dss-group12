// Settings Management

let weights = {};

// Load current weights
async function loadWeights() {
    try {
        const response = await fetch('/api/criteria-weights');
        weights = await response.json();
        
        document.getElementById('weightPeople').value = weights.people_benefitted;
        document.getElementById('weightEfficiency').value = weights.efficiency;
        document.getElementById('weightSuccess').value = weights.success_rate;
        document.getElementById('weightCost').value = weights.cost_effectiveness;
        document.getElementById('weightUrgency').value = weights.urgency;
        document.getElementById('weightSustainability').value = weights.sustainability;
        document.getElementById('weightTransparency').value = weights.transparency;
        
        updateTotalWeight();
    } catch (error) {
        showError('Không thể tải trọng số: ' + error.message);
    }
}

// Update total weight display
function updateTotalWeight() {
    const inputs = document.querySelectorAll('.weight-input');
    let total = 0;
    inputs.forEach(input => {
        total += parseFloat(input.value) || 0;
    });
    
    const totalInput = document.getElementById('totalWeight');
    totalInput.value = total.toFixed(2);
    
    // Highlight if not equal to 1
    if (Math.abs(total - 1.0) > 0.01) {
        totalInput.classList.add('is-invalid');
    } else {
        totalInput.classList.remove('is-invalid');
    }
}

// Add listeners to weight inputs
document.querySelectorAll('.weight-input').forEach(input => {
    input.addEventListener('input', updateTotalWeight);
});

// Save weights
document.getElementById('weightsForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const newWeights = {
        people_benefitted: parseFloat(document.getElementById('weightPeople').value),
        efficiency: parseFloat(document.getElementById('weightEfficiency').value),
        success_rate: parseFloat(document.getElementById('weightSuccess').value),
        cost_effectiveness: parseFloat(document.getElementById('weightCost').value),
        urgency: parseFloat(document.getElementById('weightUrgency').value),
        sustainability: parseFloat(document.getElementById('weightSustainability').value),
        transparency: parseFloat(document.getElementById('weightTransparency').value)
    };
    
    // Validate sum
    const total = Object.values(newWeights).reduce((a, b) => a + b, 0);
    if (Math.abs(total - 1.0) > 0.01) {
        showError('Tổng trọng số phải bằng 1.0');
        return;
    }
    
    try {
        const response = await fetch('/api/criteria-weights', {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(newWeights)
        });
        
        if (response.ok) {
            showSuccess('Đã cập nhật trọng số thành công');
            loadWeights();
        } else {
            const error = await response.json();
            showError(error.error);
        }
    } catch (error) {
        showError('Không thể cập nhật trọng số: ' + error.message);
    }
});

// Reset to default weights
function resetWeights() {
    document.getElementById('weightPeople').value = 0.25;
    document.getElementById('weightEfficiency').value = 0.20;
    document.getElementById('weightSuccess').value = 0.15;
    document.getElementById('weightCost').value = 0.15;
    document.getElementById('weightUrgency').value = 0.10;
    document.getElementById('weightSustainability').value = 0.10;
    document.getElementById('weightTransparency').value = 0.05;
    updateTotalWeight();
}

loadWeights();
