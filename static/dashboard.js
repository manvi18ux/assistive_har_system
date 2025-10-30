// Dashboard JavaScript - Real-time Updates and Interactions

// Initialize variables
let activityChart = null;
let activityHistory = [];
let healthScore = 85;

// Activity icons mapping
const activityIcons = {
    'Sitting': 'fa-chair',
    'Standing': 'fa-male',
    'Walking': 'fa-walking',
    'Unknown': 'fa-question-circle',
    'FALL DETECTED': 'fa-exclamation-triangle'
};

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    startRealtimeUpdates();
    initializeAnimations();
});

// Initialize Charts
function initializeCharts() {
    const ctx = document.getElementById('activityChart').getContext('2d');
    
    // Generate time labels for last 24 hours
    const labels = [];
    for (let i = 23; i >= 0; i--) {
        const hour = new Date();
        hour.setHours(hour.getHours() - i);
        labels.push(hour.getHours() + ':00');
    }
    
    activityChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Sitting',
                data: Array(24).fill(0),
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Standing',
                data: Array(24).fill(0),
                borderColor: '#f59e0b',
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Walking',
                data: Array(24).fill(0),
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#8b92b9',
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 33, 57, 0.9)',
                    titleColor: '#ffffff',
                    bodyColor: '#8b92b9',
                    borderColor: 'rgba(139, 146, 185, 0.2)',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(139, 146, 185, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#8b92b9',
                        font: {
                            size: 10
                        }
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(139, 146, 185, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#8b92b9',
                        font: {
                            size: 10
                        }
                    }
                }
            }
        }
    });
}

// Start real-time updates
function startRealtimeUpdates() {
    updateDashboard();
    setInterval(updateDashboard, 2000); // Update every 2 seconds
    setInterval(updateClock, 1000); // Update clock every second
}

// Update clock
function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    // Update any clock elements if needed
}

// Update dashboard with latest data
async function updateDashboard() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        // Update current activity
        updateActivityMonitor(data);
        
        // Update statistics
        updateStatistics(data);
        
        // Update alerts
        updateAlerts(data);
        
        // Update health score
        updateHealthScore(data);
        
        // Update risk assessment
        updateRiskAssessment(data);
        
        // Update header stats
        updateHeaderStats(data);
        
        // Check for emergencies
        checkEmergency(data);
        
        // Update chart
        updateActivityChart(data);
        
    } catch (error) {
        console.error('Error updating dashboard:', error);
    }
}

// Update activity monitor
function updateActivityMonitor(data) {
    const activityEl = document.getElementById('currentActivity');
    const durationEl = document.getElementById('activityDuration');
    const iconEl = document.getElementById('activityIcon');
    
    const activity = data.current_activity || 'Unknown';
    activityEl.textContent = activity.toUpperCase();
    
    // Update icon
    const iconClass = activityIcons[activity] || 'fa-question-circle';
    iconEl.innerHTML = `<i class="fas ${iconClass}"></i>`;
    
    // Update duration if available
    if (data.activity_duration) {
        const duration = Math.floor(data.activity_duration.current_duration || 0);
        const minutes = Math.floor(duration / 60);
        const seconds = duration % 60;
        durationEl.textContent = `Duration: ${minutes}m ${seconds}s`;
        
        // Change color based on duration thresholds
        const card = document.querySelector('.activity-monitor');
        if (activity === 'Sitting' && duration > 1800) {
            card.style.background = 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
        } else if (activity === 'Standing' && duration > 1200) {
            card.style.background = 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)';
        } else if (activity === 'Walking') {
            card.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
        } else {
            card.style.background = 'var(--gradient-1)';
        }
    }
}

// Update statistics
function updateStatistics(data) {
    if (data.activity_duration && data.activity_duration.daily_stats) {
        const stats = data.activity_duration.daily_stats;
        
        // Update sitting time
        const sittingMinutes = Math.floor((stats.total_sitting || 0) / 60);
        document.getElementById('sittingTime').textContent = `${sittingMinutes}m`;
        
        // Update walking time
        const walkingMinutes = Math.floor((stats.total_walking || 0) / 60);
        document.getElementById('walkingTime').textContent = `${walkingMinutes}m`;
        
        // Update warnings
        document.getElementById('warningCount').textContent = stats.warnings_issued || 0;
    }
    
    // Update fall count
    if (data.statistics) {
        document.getElementById('fallCount').textContent = data.statistics.falls_today || 0;
    }
}

// Update alerts
function updateAlerts(data) {
    const alertList = document.getElementById('alertList');
    
    if (data.alerts && data.alerts.length > 0) {
        alertList.innerHTML = '';
        
        data.alerts.slice(0, 5).forEach(alert => {
            const alertItem = document.createElement('div');
            alertItem.className = `alert-item ${alert.priority || 'normal'}`;
            
            const time = new Date(alert.received_at || alert.timestamp).toLocaleTimeString();
            
            alertItem.innerHTML = `
                <div class="alert-header">
                    <span class="alert-type">${alert.type.toUpperCase()}</span>
                    <span class="alert-time">${time}</span>
                </div>
                <div class="alert-message">${alert.message}</div>
            `;
            
            alertList.appendChild(alertItem);
        });
    } else {
        alertList.innerHTML = '<div class="alert-item normal"><div class="alert-message">No recent alerts</div></div>';
    }
}

// Update health score
function updateHealthScore(data) {
    // Calculate health score based on activity
    let score = 85; // Base score
    
    if (data.activity_duration && data.activity_duration.daily_stats) {
        const stats = data.activity_duration.daily_stats;
        const sittingHours = (stats.total_sitting || 0) / 3600;
        const walkingMinutes = (stats.total_walking || 0) / 60;
        
        // Decrease score for too much sitting
        if (sittingHours > 6) score -= 10;
        if (sittingHours > 8) score -= 10;
        
        // Increase score for walking
        if (walkingMinutes > 30) score += 5;
        if (walkingMinutes > 60) score += 5;
        
        // Decrease for warnings
        score -= (stats.warnings_issued || 0) * 2;
        
        // Decrease for falls
        if (data.statistics && data.statistics.falls_today > 0) {
            score -= data.statistics.falls_today * 20;
        }
    }
    
    // Clamp score between 0 and 100
    score = Math.max(0, Math.min(100, score));
    healthScore = score;
    
    // Update display
    document.getElementById('healthScore').textContent = score;
    
    // Update progress circle
    const progress = document.getElementById('healthProgress');
    const circumference = 2 * Math.PI * 90;
    const offset = circumference - (score / 100) * circumference;
    progress.style.strokeDashoffset = offset;
    
    // Change color based on score
    let color = '#10b981'; // Green
    if (score < 50) color = '#ef4444'; // Red
    else if (score < 70) color = '#f59e0b'; // Orange
    
    progress.style.stroke = color;
}

// Update risk assessment
function updateRiskAssessment(data) {
    let fallRisk = 20;
    let inactivityRisk = 40;
    let healthRisk = 15;
    
    if (data.activity_duration && data.activity_duration.daily_stats) {
        const stats = data.activity_duration.daily_stats;
        
        // Calculate inactivity risk
        const sittingHours = (stats.total_sitting || 0) / 3600;
        inactivityRisk = Math.min(100, sittingHours * 10);
        
        // Calculate health risk based on warnings
        healthRisk = Math.min(100, (stats.warnings_issued || 0) * 15);
    }
    
    // Update fall risk based on fall history
    if (data.statistics && data.statistics.falls_today > 0) {
        fallRisk = Math.min(100, 50 + data.statistics.falls_today * 25);
    }
    
    // Update UI
    updateRiskMeter('fallRisk', fallRisk);
    updateRiskMeter('inactivityRisk', inactivityRisk);
    updateRiskMeter('healthRisk', healthRisk);
}

// Update risk meter
function updateRiskMeter(id, value) {
    const element = document.getElementById(id);
    element.style.width = value + '%';
    
    // Change color based on value
    let color = '#10b981'; // Green
    if (value > 70) color = '#ef4444'; // Red
    else if (value > 40) color = '#f59e0b'; // Orange
    
    element.style.background = color;
    
    // Update risk value text
    const parent = element.parentElement.parentElement;
    const valueEl = parent.querySelector('.risk-value');
    if (valueEl) {
        let riskLevel = 'Low';
        if (value > 70) riskLevel = 'High';
        else if (value > 40) riskLevel = 'Medium';
        valueEl.textContent = riskLevel;
    }
}

// Update header stats
function updateHeaderStats(data) {
    // Update active alerts count
    const alertCount = data.alerts ? data.alerts.filter(a => 
        (Date.now() - new Date(a.received_at || a.timestamp).getTime()) < 300000
    ).length : 0;
    
    document.getElementById('headerAlerts').textContent = alertCount;
    
    // Update system status
    const statusEl = document.getElementById('headerStatus');
    if (data.system_status === 'Active') {
        statusEl.innerHTML = '<i class="fas fa-circle" style="color: #10b981;"></i> Live';
    } else {
        statusEl.innerHTML = '<i class="fas fa-circle" style="color: #ef4444;"></i> Offline';
    }
}

// Check for emergencies
function checkEmergency(data) {
    const emergencyAlert = document.getElementById('emergencyAlert');
    
    // Check for recent critical alerts
    const hasEmergency = data.alerts && data.alerts.some(alert => 
        alert.priority === 'critical' && 
        (Date.now() - new Date(alert.received_at || alert.timestamp).getTime()) < 30000
    );
    
    if (hasEmergency) {
        emergencyAlert.classList.add('active');
        // Show toast notification
        showToast('Emergency Alert', 'Critical situation detected!', 'danger');
    } else {
        emergencyAlert.classList.remove('active');
    }
}

// Update activity chart
function updateActivityChart(data) {
    if (!activityChart || !data.activity_duration) return;
    
    const stats = data.activity_duration.daily_stats;
    if (!stats) return;
    
    // Add new data point
    const currentHour = new Date().getHours();
    
    // Update current hour data
    activityChart.data.datasets[0].data[currentHour] = Math.floor((stats.total_sitting || 0) / 60);
    activityChart.data.datasets[1].data[currentHour] = Math.floor((stats.total_standing || 0) / 60);
    activityChart.data.datasets[2].data[currentHour] = Math.floor((stats.total_walking || 0) / 60);
    
    activityChart.update('none'); // Update without animation for smooth real-time updates
}

// Show toast notification
function showToast(title, message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-header">
            <span class="toast-title">${title}</span>
            <span class="toast-close" onclick="this.parentElement.parentElement.remove()">×</span>
        </div>
        <div class="toast-message">${message}</div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// Initialize animations
function initializeAnimations() {
    // Add stagger animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
    
    // Add hover effects
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// Export functions for external use
window.dashboardFunctions = {
    showToast,
    updateHealthScore,
    updateRiskAssessment
};
