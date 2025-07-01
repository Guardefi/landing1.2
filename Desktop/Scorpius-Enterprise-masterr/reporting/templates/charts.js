// Scorpius Enterprise Reporting - Chart Components
// Chart.js configuration and utilities for security reports

// Chart color schemes
const SEVERITY_COLORS = {
    CRITICAL: '#dc2626',
    HIGH: '#ea580c',
    MEDIUM: '#d97706',
    LOW: '#16a34a',
    INFO: '#2563eb'
};

const CHART_COLORS = {
    primary: '#3b82f6',
    secondary: '#6b7280',
    success: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
    info: '#06b6d4'
};

// Default chart options
const DEFAULT_CHART_OPTIONS = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'bottom',
            labels: {
                padding: 20,
                usePointStyle: true,
                font: {
                    family: 'Inter, sans-serif',
                    size: 12
                }
            }
        },
        tooltip: {
            backgroundColor: 'rgba(17, 24, 39, 0.95)',
            titleColor: '#f9fafb',
            bodyColor: '#f9fafb',
            borderColor: '#374151',
            borderWidth: 1,
            cornerRadius: 8,
            padding: 12,
            titleFont: {
                family: 'Inter, sans-serif',
                size: 14,
                weight: '600'
            },
            bodyFont: {
                family: 'Inter, sans-serif',
                size: 13
            }
        }
    }
};

// Severity Distribution Pie Chart
function createSeverityChart(canvasId, severityData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas with ID '${canvasId}' not found`);
        return null;
    }

    const labels = Object.keys(severityData);
    const data = Object.values(severityData);
    const colors = labels.map(label => SEVERITY_COLORS[label.toUpperCase()] || CHART_COLORS.secondary);

    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderColor: '#ffffff',
                borderWidth: 2,
                hoverBorderWidth: 3
            }]
        },
        options: {
            ...DEFAULT_CHART_OPTIONS,
            cutout: '60%',
            plugins: {
                ...DEFAULT_CHART_OPTIONS.plugins,
                legend: {
                    ...DEFAULT_CHART_OPTIONS.plugins.legend,
                    position: 'right'
                },
                tooltip: {
                    ...DEFAULT_CHART_OPTIONS.plugins.tooltip,
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed * 100) / total).toFixed(1);
                            return `${context.label}: ${context.parsed} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Finding Types Bar Chart
function createFindingTypesChart(canvasId, typeData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas with ID '${canvasId}' not found`);
        return null;
    }

    const labels = Object.keys(typeData);
    const data = Object.values(typeData);

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Findings',
                data: data,
                backgroundColor: CHART_COLORS.primary,
                borderColor: CHART_COLORS.primary,
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }]
        },
        options: {
            ...DEFAULT_CHART_OPTIONS,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        color: '#6b7280',
                        font: {
                            family: 'Inter, sans-serif',
                            size: 11
                        }
                    },
                    grid: {
                        color: '#f3f4f6'
                    }
                },
                x: {
                    ticks: {
                        color: '#6b7280',
                        font: {
                            family: 'Inter, sans-serif',
                            size: 11
                        },
                        maxRotation: 45,
                        minRotation: 0
                    },
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                ...DEFAULT_CHART_OPTIONS.plugins,
                legend: {
                    display: false
                }
            }
        }
    });
}

// Risk Score Timeline Chart
function createRiskTimelineChart(canvasId, timelineData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas with ID '${canvasId}' not found`);
        return null;
    }

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: timelineData.labels,
            datasets: [{
                label: 'Risk Score',
                data: timelineData.scores,
                borderColor: CHART_COLORS.danger,
                backgroundColor: CHART_COLORS.danger + '20',
                borderWidth: 3,
                fill: true,
                tension: 0.3,
                pointBackgroundColor: CHART_COLORS.danger,
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            ...DEFAULT_CHART_OPTIONS,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 10,
                    ticks: {
                        color: '#6b7280',
                        font: {
                            family: 'Inter, sans-serif',
                            size: 11
                        }
                    },
                    grid: {
                        color: '#f3f4f6'
                    },
                    title: {
                        display: true,
                        text: 'Risk Score',
                        color: '#374151',
                        font: {
                            family: 'Inter, sans-serif',
                            size: 12,
                            weight: '600'
                        }
                    }
                },
                x: {
                    ticks: {
                        color: '#6b7280',
                        font: {
                            family: 'Inter, sans-serif',
                            size: 11
                        }
                    },
                    grid: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Scan Date',
                        color: '#374151',
                        font: {
                            family: 'Inter, sans-serif',
                            size: 12,
                            weight: '600'
                        }
                    }
                }
            }
        }
    });
}

// Function Coverage Heatmap (simplified as a bar chart)
function createCoverageChart(canvasId, coverageData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas with ID '${canvasId}' not found`);
        return null;
    }

    const labels = coverageData.map(item => item.function);
    const coverage = coverageData.map(item => item.coverage);
    const colors = coverage.map(c => {
        if (c >= 80) return CHART_COLORS.success;
        if (c >= 60) return CHART_COLORS.warning;
        return CHART_COLORS.danger;
    });

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Coverage %',
                data: coverage,
                backgroundColor: colors,
                borderColor: colors,
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }]
        },
        options: {
            ...DEFAULT_CHART_OPTIONS,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        },
                        color: '#6b7280',
                        font: {
                            family: 'Inter, sans-serif',
                            size: 11
                        }
                    },
                    grid: {
                        color: '#f3f4f6'
                    }
                },
                y: {
                    ticks: {
                        color: '#6b7280',
                        font: {
                            family: 'Inter, sans-serif',
                            size: 10
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                ...DEFAULT_CHART_OPTIONS.plugins,
                legend: {
                    display: false
                },
                tooltip: {
                    ...DEFAULT_CHART_OPTIONS.plugins.tooltip,
                    callbacks: {
                        label: function(context) {
                            return `Coverage: ${context.parsed.x}%`;
                        }
                    }
                }
            }
        }
    });
}

// Gas Usage Analysis Chart
function createGasAnalysisChart(canvasId, gasData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas with ID '${canvasId}' not found`);
        return null;
    }

    return new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Gas Usage',
                data: gasData,
                backgroundColor: CHART_COLORS.info + '80',
                borderColor: CHART_COLORS.info,
                borderWidth: 2,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            ...DEFAULT_CHART_OPTIONS,
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'Function Complexity',
                        color: '#374151',
                        font: {
                            family: 'Inter, sans-serif',
                            size: 12,
                            weight: '600'
                        }
                    },
                    ticks: {
                        color: '#6b7280',
                        font: {
                            family: 'Inter, sans-serif',
                            size: 11
                        }
                    },
                    grid: {
                        color: '#f3f4f6'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Gas Cost',
                        color: '#374151',
                        font: {
                            family: 'Inter, sans-serif',
                            size: 12,
                            weight: '600'
                        }
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        },
                        color: '#6b7280',
                        font: {
                            family: 'Inter, sans-serif',
                            size: 11
                        }
                    },
                    grid: {
                        color: '#f3f4f6'
                    }
                }
            },
            plugins: {
                ...DEFAULT_CHART_OPTIONS.plugins,
                tooltip: {
                    ...DEFAULT_CHART_OPTIONS.plugins.tooltip,
                    callbacks: {
                        label: function(context) {
                            return `Complexity: ${context.parsed.x}, Gas: ${context.parsed.y.toLocaleString()}`;
                        }
                    }
                }
            }
        }
    });
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js library not loaded. Charts will not be rendered.');
        return;
    }

    // Set global defaults
    Chart.defaults.font.family = 'Inter, sans-serif';
    Chart.defaults.color = '#6b7280';

    // Auto-initialize charts based on data attributes
    const chartElements = document.querySelectorAll('[data-chart]');
    chartElements.forEach(function(element) {
        const chartType = element.getAttribute('data-chart');
        const chartData = element.getAttribute('data-chart-data');
        
        if (chartData) {
            try {
                const data = JSON.parse(chartData);
                const canvasId = element.id;
                
                switch (chartType) {
                    case 'severity':
                        createSeverityChart(canvasId, data);
                        break;
                    case 'types':
                        createFindingTypesChart(canvasId, data);
                        break;
                    case 'timeline':
                        createRiskTimelineChart(canvasId, data);
                        break;
                    case 'coverage':
                        createCoverageChart(canvasId, data);
                        break;
                    case 'gas':
                        createGasAnalysisChart(canvasId, data);
                        break;
                    default:
                        console.warn(`Unknown chart type: ${chartType}`);
                }
            } catch (error) {
                console.error(`Error parsing chart data for ${element.id}:`, error);
            }
        }
    });
});

// Export functions for manual chart creation
window.ScorpiusCharts = {
    createSeverityChart,
    createFindingTypesChart,
    createRiskTimelineChart,
    createCoverageChart,
    createGasAnalysisChart,
    SEVERITY_COLORS,
    CHART_COLORS
};

