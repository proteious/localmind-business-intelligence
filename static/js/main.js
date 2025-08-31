// LocalMind Business Intelligence Agent - Frontend JavaScript

// Utility functions
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = 'block';
    }
}

function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = 'none';
    }
}

function showResults(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.add('show');
    }
}

function showAlert(message, type = 'error') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Remove alert after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Competitor Analysis Functions
async function analyzeCompetitors() {
    const location = document.getElementById('location').value;
    const businessType = document.getElementById('business_type').value;
    
    if (!location || !businessType) {
        showAlert('Please fill in all fields', 'error');
        return;
    }
    
    showLoading('loading-competitors');
    hideResults('competitors-results');
    
    try {
        const response = await fetch('/api/analyze-competitors', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                location: location,
                business_type: businessType
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayCompetitorResults(data.competitors, data.analysis);
            showResults('competitors-results');
        } else {
            showAlert(data.error || 'Analysis failed', 'error');
        }
    } catch (error) {
        showAlert('Network error. Please try again.', 'error');
    } finally {
        hideLoading('loading-competitors');
    }
}

function displayCompetitorResults(competitors, analysis) {
    const resultsDiv = document.getElementById('competitor-list');
    const statsDiv = document.getElementById('competitor-stats');
    
    // Display statistics
    statsDiv.innerHTML = `
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">${competitors.length}</div>
                <div class="stat-label">Competitors Found</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${analysis.market_density}</div>
                <div class="stat-label">Market Density</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${analysis.competition_level}</div>
                <div class="stat-label">Competition Level</div>
            </div>
        </div>
    `;
    
    // Display competitor list
    resultsDiv.innerHTML = competitors.map(competitor => `
        <div class="competitor-item">
            <div class="competitor-name">${competitor.name}</div>
            <div class="competitor-details">
                <strong>Category:</strong> ${competitor.category} | 
                <strong>Distance:</strong> ${competitor.distance}m | 
                <strong>Address:</strong> ${competitor.address}
            </div>
        </div>
    `).join('');
}

// Hours Optimization Functions
async function optimizeHours() {
    const location = document.getElementById('hours-location').value;
    const businessType = document.getElementById('hours-business-type').value;
    
    if (!location || !businessType) {
        showAlert('Please fill in all fields', 'error');
        return;
    }
    
    showLoading('loading-hours');
    hideResults('hours-results');
    
    try {
        const response = await fetch('/api/optimize-hours', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                location: location,
                business_type: businessType
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayHoursResults(data.recommendation);
            showResults('hours-results');
        } else {
            showAlert(data.error || 'Optimization failed', 'error');
        }
    } catch (error) {
        showAlert('Network error. Please try again.', 'error');
    } finally {
        hideLoading('loading-hours');
    }
}

function displayHoursResults(recommendation) {
    const resultsDiv = document.getElementById('hours-recommendation');
    
    resultsDiv.innerHTML = `
        <div class="card">
            <h3 class="card-title">📅 Recommended Operating Hours</h3>
            <div class="hours-grid">
                ${Object.entries(recommendation.weekly_schedule).map(([day, hours]) => `
                    <div class="day-hours">
                        <strong>${day}:</strong> ${hours}
                    </div>
                `).join('')}
            </div>
            <div class="insights mt-2">
                <h4>💡 Key Insights:</h4>
                <ul>
                    ${recommendation.insights.map(insight => `<li>${insight}</li>`).join('')}
                </ul>
            </div>
        </div>
    `;
}

// Market Scanner Functions
async function scanMarket() {
    const location = document.getElementById('scanner-location').value;
    const radius = document.getElementById('scanner-radius').value || 1000;
    
    if (!location) {
        showAlert('Please enter a location', 'error');
        return;
    }
    
    showLoading('loading-scanner');
    hideResults('scanner-results');
    
    try {
        const response = await fetch('/api/scan-market', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                location: location,
                radius: parseInt(radius)
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayMarketResults(data.market_data, data.opportunities);
            showResults('scanner-results');
        } else {
            showAlert(data.error || 'Market scan failed', 'error');
        }
    } catch (error) {
        showAlert('Network error. Please try again.', 'error');
    } finally {
        hideLoading('loading-scanner');
    }
}

function displayMarketResults(marketData, opportunities) {
    const resultsDiv = document.getElementById('market-opportunities');
    
    resultsDiv.innerHTML = `
        <div class="card">
            <h3 class="card-title">🎯 Market Overview</h3>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">${marketData.total_businesses}</div>
                    <div class="stat-label">Total Businesses</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${marketData.market_score}/10</div>
                    <div class="stat-label">Market Score</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3 class="card-title">🚀 Business Opportunities</h3>
            <div class="opportunities-list">
                ${opportunities.map(opp => `
                    <div class="opportunity-item">
                        <h4>${opp.category}</h4>
                        <p><strong>Opportunity Score:</strong> ${opp.score}/10</p>
                        <p>${opp.description}</p>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

// Helper function to hide results
function hideResults(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.remove('show');
    }
}

// Initialize page functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add any page-specific initialization here
    console.log('LocalMind Business Intelligence Agent loaded');
    
    // Add form submission handlers
    const competitorForm = document.getElementById('competitor-form');
    if (competitorForm) {
        competitorForm.addEventListener('submit', function(e) {
            e.preventDefault();
            analyzeCompetitors();
        });
    }
    
    const hoursForm = document.getElementById('hours-form');
    if (hoursForm) {
        hoursForm.addEventListener('submit', function(e) {
            e.preventDefault();
            optimizeHours();
        });
    }
    
    const scannerForm = document.getElementById('scanner-form');
    if (scannerForm) {
        scannerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            scanMarket();
        });
    }
});