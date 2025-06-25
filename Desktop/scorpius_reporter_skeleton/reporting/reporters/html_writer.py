"""
HTML Report Writer
==================

Generate comprehensive HTML reports with interactive charts and modern styling.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .base import ReportContext, TemplatedReporter


class HTMLReporter(TemplatedReporter):
    """HTML report generator with interactive features"""
    
    def __init__(self, output_dir: Optional[Path] = None, template_dir: Optional[Path] = None):
        super().__init__(output_dir, template_dir)
        self.supported_formats = ["html"]
        
        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Register custom filters
        self._register_filters()
        
    def _register_filters(self) -> None:
        """Register custom Jinja2 filters for HTML reports"""
        
        def severity_badge(severity: str) -> str:
            """Generate severity badge HTML"""
            colors = {
                "critical": "bg-red-600",
                "high": "bg-orange-600", 
                "medium": "bg-yellow-600",
                "low": "bg-green-600",
                "info": "bg-blue-600"
            }
            color_class = colors.get(severity.lower(), "bg-gray-600")
            return f'<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium text-white {color_class}">{severity.upper()}</span>'
            
        def risk_score_bar(score: float, max_score: float = 10.0) -> str:
            """Generate risk score progress bar"""
            percentage = (score / max_score) * 100
            if percentage >= 80:
                color = "bg-red-500"
            elif percentage >= 60:
                color = "bg-orange-500"
            elif percentage >= 40:
                color = "bg-yellow-500"
            else:
                color = "bg-green-500"
                
            return f'''
            <div class="w-full bg-gray-200 rounded-full h-2.5">
                <div class="{color} h-2.5 rounded-full transition-all duration-300" style="width: {percentage}%"></div>
            </div>
            <span class="text-sm font-medium text-gray-700">{score:.1f}/{max_score}</span>
            '''
            
        def code_highlight(code: str, language: str = "solidity") -> str:
            """Apply syntax highlighting to code"""
            # Basic syntax highlighting for Solidity
            if not code:
                return ""
                
            # This is a simplified version - in production you'd use a proper syntax highlighter
            code = code.replace("function", "<span class='text-blue-600 font-semibold'>function</span>")
            code = code.replace("contract", "<span class='text-purple-600 font-semibold'>contract</span>")
            code = code.replace("require", "<span class='text-red-600 font-semibold'>require</span>")
            code = code.replace("return", "<span class='text-green-600 font-semibold'>return</span>")
            
            return f'<pre class="bg-gray-100 p-4 rounded-lg overflow-x-auto"><code class="language-{language}">{code}</code></pre>'
            
        def format_timestamp(timestamp: str) -> str:
            """Format timestamp for display"""
            from datetime import datetime
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
            except Exception:
                return timestamp
                
        def json_pretty(value: Any) -> str:
            """Pretty print JSON data"""
            return json.dumps(value, indent=2, default=str)
            
        # Register all filters
        self.jinja_env.filters['severity_badge'] = severity_badge
        self.jinja_env.filters['risk_score_bar'] = risk_score_bar
        self.jinja_env.filters['code_highlight'] = code_highlight
        self.jinja_env.filters['format_timestamp'] = format_timestamp
        self.jinja_env.filters['json_pretty'] = json_pretty
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render Jinja2 template with context"""
        template = self.jinja_env.get_template(template_name)
        return template.render(**context)
        
    async def generate(
        self,
        context: ReportContext,
        output_path: Optional[Path] = None,
        template_name: str = "base.html",
        include_charts: bool = True,
        dark_theme: bool = False,
        **kwargs
    ) -> Path:
        """
        Generate HTML report.
        
        Args:
            context: Report context with scan data
            output_path: Optional custom output path
            template_name: Jinja2 template to use
            include_charts: Whether to include interactive charts
            dark_theme: Use dark theme styling
            **kwargs: Additional template variables
        """
        # Validate context
        errors = await self.validate_context(context)
        if errors:
            raise ValueError(f"Context validation failed: {'; '.join(errors)}")
            
        # Prepare output path
        if not output_path:
            filename = self.get_default_filename(context)
            output_path = self.output_dir / filename
            
        # Prepare template context
        template_context = self.prepare_template_context(context)
        
        # Add HTML-specific context
        template_context.update({
            "include_charts": include_charts,
            "dark_theme": dark_theme,
            "chart_data_json": json.dumps(template_context["charts"], default=self._json_serializer),
            **kwargs
        })
        
        # Generate charts JavaScript if requested
        if include_charts:
            template_context["charts_js"] = self._generate_charts_js(template_context["charts"])
            
        # Render template
        try:
            html_content = self.render_template(template_name, template_context)
        except Exception as e:
            # Fallback to default template if custom template fails
            if template_name != "default_report.html":
                # Create default template if it doesn't exist
                if not (self.template_dir / "default_report.html").exists():
                    create_default_template(self.template_dir)
                html_content = self.render_template("default_report.html", template_context)
            else:
                # If we still can't find the default template, create it
                if not (self.template_dir / "default_report.html").exists():
                    create_default_template(self.template_dir)
                    html_content = self.render_template("default_report.html", template_context)
                else:
                    raise e
                
        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return output_path
        
    def _json_serializer(self, obj):
        """Custom JSON serializer for complex objects like datetime"""
        from datetime import datetime
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)

    def get_file_extension(self) -> str:
        """Get file extension for HTML reports"""
        return "html"
        
    def _generate_charts_js(self, charts_data: Dict[str, Any]) -> str:
        """Generate JavaScript code for interactive charts"""
        
        js_code = """
        // Chart.js configuration and initialization
        document.addEventListener('DOMContentLoaded', function() {
            // Severity Distribution Pie Chart
            const severityCtx = document.getElementById('severityChart');
            if (severityCtx) {
                new Chart(severityCtx, {
                    type: 'doughnut',
                    data: {
                        labels: """ + json.dumps(charts_data["severity_distribution"]["labels"]) + """,
                        datasets: [{
                            data: """ + json.dumps(charts_data["severity_distribution"]["values"]) + """,
                            backgroundColor: """ + json.dumps(charts_data["severity_distribution"]["colors"]) + """,
                            borderWidth: 2,
                            borderColor: '#ffffff'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: {
                                    padding: 20,
                                    usePointStyle: true
                                }
                            },
                            title: {
                                display: true,
                                text: 'Vulnerability Distribution by Severity',
                                font: { size: 16, weight: 'bold' }
                            }
                        }
                    }
                });
            }
            
            // Timeline Chart
            const timelineCtx = document.getElementById('timelineChart');
            if (timelineCtx && """ + json.dumps(len(charts_data["timeline"]) > 1) + """) {
                const timelineData = """ + json.dumps(charts_data["timeline"]) + """;
                
                new Chart(timelineCtx, {
                    type: 'line',
                    data: {
                        labels: timelineData.map(d => d.date),
                        datasets: [
                            {
                                label: 'Critical',
                                data: timelineData.map(d => d.critical),
                                borderColor: '#dc2626',
                                backgroundColor: 'rgba(220, 38, 38, 0.1)',
                                tension: 0.3
                            },
                            {
                                label: 'High',
                                data: timelineData.map(d => d.high),
                                borderColor: '#ea580c',
                                backgroundColor: 'rgba(234, 88, 12, 0.1)',
                                tension: 0.3
                            },
                            {
                                label: 'Medium',
                                data: timelineData.map(d => d.medium),
                                borderColor: '#d97706',
                                backgroundColor: 'rgba(217, 119, 6, 0.1)',
                                tension: 0.3
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            title: {
                                display: true,
                                text: 'Vulnerability Trends Over Time',
                                font: { size: 16, weight: 'bold' }
                            },
                            legend: {
                                position: 'top'
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: 'Number of Issues'
                                }
                            },
                            x: {
                                title: {
                                    display: true,
                                    text: 'Scan Date'
                                }
                            }
                        }
                    }
                });
            }
            
            // Risk Score Chart
            const riskCtx = document.getElementById('riskChart');
            if (riskCtx) {
                const riskData = """ + json.dumps(charts_data["risk_scores"]) + """;
                
                new Chart(riskCtx, {
                    type: 'bar',
                    data: {
                        labels: riskData.map(d => d.project),
                        datasets: [{
                            label: 'Risk Score',
                            data: riskData.map(d => d.risk_score),
                            backgroundColor: riskData.map(d => {
                                if (d.overall_risk === 'critical') return '#dc2626';
                                if (d.overall_risk === 'high') return '#ea580c';
                                if (d.overall_risk === 'medium') return '#d97706';
                                return '#65a30d';
                            }),
                            borderRadius: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            title: {
                                display: true,
                                text: 'Risk Score by Project',
                                font: { size: 16, weight: 'bold' }
                            },
                            legend: {
                                display: false
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 10,
                                title: {
                                    display: true,
                                    text: 'Risk Score (0-10)'
                                }
                            }
                        }
                    }
                });
            }
            
            // Interactive features
            initializeInteractiveFeatures();
        });
        
        function initializeInteractiveFeatures() {
            // Collapsible sections
            const toggleButtons = document.querySelectorAll('[data-toggle="collapse"]');
            toggleButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const target = document.querySelector(this.getAttribute('data-target'));
                    if (target) {
                        target.classList.toggle('hidden');
                        const icon = this.querySelector('.toggle-icon');
                        if (icon) {
                            icon.classList.toggle('rotate-180');
                        }
                    }
                });
            });
            
            // Severity filtering
            const severityFilters = document.querySelectorAll('[data-severity-filter]');
            severityFilters.forEach(filter => {
                filter.addEventListener('change', function() {
                    const severity = this.getAttribute('data-severity-filter');
                    const items = document.querySelectorAll('[data-severity]');
                    
                    items.forEach(item => {
                        if (this.checked) {
                            if (item.getAttribute('data-severity') === severity) {
                                item.style.display = '';
                            }
                        } else {
                            if (item.getAttribute('data-severity') === severity) {
                                item.style.display = 'none';
                            }
                        }
                    });
                });
            });
            
            // Search functionality
            const searchInput = document.getElementById('vulnerabilitySearch');
            if (searchInput) {
                searchInput.addEventListener('input', function() {
                    const searchTerm = this.value.toLowerCase();
                    const vulnerabilities = document.querySelectorAll('.vulnerability-item');
                    
                    vulnerabilities.forEach(vuln => {
                        const text = vuln.textContent.toLowerCase();
                        vuln.style.display = text.includes(searchTerm) ? '' : 'none';
                    });
                });
            }
        }
        """
        
        return js_code


# Create default HTML template if it doesn't exist
def create_default_template(template_dir: Path) -> None:
    """Create default HTML template file"""
    template_dir.mkdir(parents=True, exist_ok=True)
    
    default_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ metadata.title }}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .chart-container { height: 400px; }
        .vulnerability-item { transition: all 0.3s ease; }
        .vulnerability-item:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .rotate-180 { transform: rotate(180deg); }
        {% if dark_theme %}
        body { background-color: #1f2937; color: #f9fafb; }
        .bg-white { background-color: #374151 !important; }
        .text-gray-900 { color: #f9fafb !important; }
        .border-gray-200 { border-color: #4b5563 !important; }
        {% endif %}
    </style>
</head>
<body class="bg-gray-50 font-sans">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-3xl font-bold text-gray-900">{{ metadata.title }}</h1>
                    <p class="text-gray-600 mt-1">{{ metadata.description }}</p>
                </div>
                <div class="text-right">
                    <p class="text-sm text-gray-500">Generated: {{ generated_at | format_timestamp }}</p>
                    <p class="text-sm text-gray-500">Version: {{ metadata.version }}</p>
                </div>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- Executive Summary -->
        <section class="bg-white rounded-lg shadow p-6 mb-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Executive Summary</h2>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div class="text-center p-4 bg-red-50 rounded-lg">
                    <div class="text-3xl font-bold text-red-600">{{ stats.critical_issues }}</div>
                    <div class="text-sm text-red-600">Critical</div>
                </div>
                <div class="text-center p-4 bg-orange-50 rounded-lg">
                    <div class="text-3xl font-bold text-orange-600">{{ stats.high_issues }}</div>
                    <div class="text-sm text-orange-600">High</div>
                </div>
                <div class="text-center p-4 bg-yellow-50 rounded-lg">
                    <div class="text-3xl font-bold text-yellow-600">{{ stats.medium_issues }}</div>
                    <div class="text-sm text-yellow-600">Medium</div>
                </div>
                <div class="text-center p-4 bg-green-50 rounded-lg">
                    <div class="text-3xl font-bold text-green-600">{{ stats.low_issues + stats.info_issues }}</div>
                    <div class="text-sm text-green-600">Low/Info</div>
                </div>
            </div>
        </section>

        {% if include_charts %}
        <!-- Charts Section -->
        <section class="bg-white rounded-lg shadow p-6 mb-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-6">Vulnerability Analysis</h2>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div class="chart-container">
                    <canvas id="severityChart"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="riskChart"></canvas>
                </div>
            </div>
            {% if stats.total_scans > 1 %}
            <div class="mt-8 chart-container">
                <canvas id="timelineChart"></canvas>
            </div>
            {% endif %}
        </section>
        {% endif %}

        <!-- Vulnerabilities -->
        <section class="bg-white rounded-lg shadow p-6 mb-8">
            <div class="flex items-center justify-between mb-6">
                <h2 class="text-2xl font-bold text-gray-900">Detailed Findings</h2>
                <input type="text" id="vulnerabilitySearch" placeholder="Search vulnerabilities..." 
                       class="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500">
            </div>
            
            {% for scan in scan_results %}
            <div class="mb-8">
                <h3 class="text-xl font-semibold text-gray-800 mb-4">{{ scan.project_name }}</h3>
                
                {% for vuln in scan.vulnerabilities %}
                <div class="vulnerability-item bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4" data-severity="{{ vuln.severity }}">
                    <div class="flex items-start justify-between mb-2">
                        <h4 class="text-lg font-medium text-gray-900">{{ vuln.title }}</h4>
                        {{ vuln.severity | severity_badge }}
                    </div>
                    
                    <p class="text-gray-700 mb-3">{{ vuln.description }}</p>
                    
                    {% if vuln.code_snippet %}
                    <div class="mb-3">
                        <h5 class="font-medium text-gray-800 mb-2">Code Location:</h5>
                        {{ vuln.code_snippet | code_highlight }}
                    </div>
                    {% endif %}
                    
                    {% if vuln.recommendation %}
                    <div class="bg-blue-50 border border-blue-200 rounded p-3">
                        <h5 class="font-medium text-blue-800 mb-1">Recommendation:</h5>
                        <p class="text-blue-700">{{ vuln.recommendation }}</p>
                    </div>
                    {% endif %}
                    
                    <div class="mt-3 flex items-center space-x-4 text-sm text-gray-500">
                        <span>Risk Score: {{ vuln.risk_score }}/10</span>
                        <span>Confidence: {{ (vuln.confidence * 100) | round(1) }}%</span>
                        {% if vuln.function_name %}<span>Function: {{ vuln.function_name }}</span>{% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
            {% endfor %}
        </section>

        <!-- Scan Details -->
        <section class="bg-white rounded-lg shadow p-6">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Scan Details</h2>
            {% for scan in scan_results %}
            <div class="border-b border-gray-200 pb-4 mb-4 last:border-b-0">
                <h3 class="text-lg font-semibold text-gray-800">{{ scan.project_name }}</h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-2 text-sm">
                    <div><span class="font-medium">Scan ID:</span> {{ scan.id }}</div>
                    <div><span class="font-medium">Created:</span> {{ scan.created_at | format_timestamp }}</div>
                    <div><span class="font-medium">Status:</span> {{ scan.status }}</div>
                    <div><span class="font-medium">Contracts:</span> {{ scan.contracts | length }}</div>
                </div>
            </div>
            {% endfor %}
        </section>
    </main>

    {% if include_charts %}
    <script>
        {{ charts_js }}
    </script>
    {% endif %}
</body>
</html>'''
    
    template_path = template_dir / "default_report.html"
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(default_template)

