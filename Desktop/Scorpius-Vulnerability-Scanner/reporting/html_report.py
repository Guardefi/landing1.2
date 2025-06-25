"""HTML Report Generator for Scorpius Vulnerability Scanner

This module provides functionality for generating HTML vulnerability reports
with interactive elements and visualization capabilities.
"""

import os
import json
import logging
import datetime
from typing import Dict, Any, List

from reporting.report_generator import ReportGenerator

logger = logging.getLogger("scorpius.reporting.html")


class HtmlReportGenerator(ReportGenerator):
    """HTML report generator
    
    Generates visually appealing HTML reports with interactive elements.
    """
    
    def generate(self, scan_results: Dict[str, Any], output_path: str) -> str:
        """Generate an HTML report
        
        Args:
            scan_results: The scan results to generate a report from
            output_path: Path to save the report to
            
        Returns:
            str: Path to the generated report
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Generate the HTML content
        html_content = self._generate_html_content(scan_results)
        
        # Write the report to the output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        logger.info(f"HTML report generated: {output_path}")
        return output_path
    
    def _generate_html_content(self, scan_results: Dict[str, Any]) -> str:
        """Generate the HTML content for the report
        
        Args:
            scan_results: The scan results
            
        Returns:
            str: HTML content
        """
        # Get scan metadata
        metadata = {
            "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "scanner_version": scan_results.get("scanner_version", "unknown"),
            "scan_duration": scan_results.get("scan_duration", 0),
            "plugins_used": scan_results.get("plugins_used", [])
        }
        
        # Get target information
        target = scan_results.get("target", {})
        target_name = target.get("name", "Unknown Target")
        
        # Get findings
        findings = scan_results.get("findings", [])
        
        # Generate summary
        summary = self._generate_summary(scan_results)
        
        # Start building HTML content
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scorpius Vulnerability Report - {target_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            color: #333;
            background-color: #f5f5f5;
        }}
        .container {{
            max-inline-size: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 5px 5px 0 0;
        }}
        .summary-card {{
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            padding: 20px;
            margin-block-end: 20px;
        }}
        .severity-chart {{
            display: flex;
            margin: 20px 0;
        }}
        .severity-bar {{
            block-size: 30px;
            margin-inline-end: 2px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }}
        .critical {{ background-color: #e74c3c; }}
        .high {{ background-color: #e67e22; }}
        .medium {{ background-color: #f39c12; }}
        .low {{ background-color: #3498db; }}
        .info {{ background-color: #2ecc71; }}
        .finding-card {{
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            padding: 20px;
            margin-block-end: 10px;
        }}
        .finding-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-block-end: 10px;
        }}
        .finding-title {{
            font-size: 18px;
            font-weight: bold;
        }}
        .finding-severity {{
            padding: 5px 10px;
            border-radius: 3px;
            color: white;
            font-weight: bold;
        }}
        .code-block {{
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 3px;
            padding: 10px;
            overflow-x: auto;
            font-family: 'Courier New', Courier, monospace;
        }}
        .metadata {{
            display: flex;
            flex-wrap: wrap;
            margin-block-start: 10px;
        }}
        .metadata-item {{
            margin-inline-end: 20px;
            margin-block-end: 10px;
        }}
        .metadata-label {{
            font-weight: bold;
            margin-inline-end: 5px;
        }}
        table {{
            inline-size: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            text-align: start;
            padding: 8px;
            border-block-end: 1px solid #ddd;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        .risk-score {{
            font-size: 24px;
            font-weight: bold;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Scorpius Vulnerability Report</h1>
            <p>Generated on {metadata['generated_at']}</p>
        </header>
        
        <div class="summary-card">
            <h2>Target: {target_name}</h2>
            <div class="metadata">
                <div class="metadata-item">
                    <span class="metadata-label">Scanner Version:</span>
                    <span>{metadata['scanner_version']}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Scan Duration:</span>
                    <span>{metadata['scan_duration']} seconds</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Status:</span>
                    <span>{summary['scan_status']}</span>
                </div>
            </div>
        </div>
        
        <div class="summary-card">
            <h2>Risk Overview</h2>
            <div class="risk-score">
                Risk Score: {summary['risk_score']} / 10.0
            </div>
            <h3>Findings by Severity</h3>
            <div class="severity-chart">
"""

        # Add severity bars
        severity_counts = summary.get("severity_counts", {})
        total_findings = summary.get("total_findings", 0)
        if total_findings > 0:
            for severity, count in severity_counts.items():
                percentage = (count / total_findings) * 100
                html += f"""
                <div class="severity-bar {severity.lower()}" style="inline-size: {percentage}%">
                    {count} {severity}
                </div>"""

        html += """
            </div>
            <h3>Summary of Findings</h3>
            <table>
                <tr>
                    <th>Severity</th>
                    <th>Count</th>
                </tr>
"""

        # Add severity count rows
        for severity, count in severity_counts.items():
            html += f"""
                <tr>
                    <td>{severity.capitalize()}</td>
                    <td>{count}</td>
                </tr>"""

        html += """
            </table>
            
            <h3>Findings by Type</h3>
            <table>
                <tr>
                    <th>Vulnerability Type</th>
                    <th>Count</th>
                </tr>
"""

        # Add vuln type count rows
        vuln_type_counts = summary.get("vulnerability_type_counts", {})
        for vuln_type, count in vuln_type_counts.items():
            html += f"""
                <tr>
                    <td>{vuln_type}</td>
                    <td>{count}</td>
                </tr>"""

        html += """
            </table>
        </div>
        
        <h2>Detailed Findings</h2>
"""

        # Add detailed findings
        for finding in findings:
            severity = finding.get("severity", "unknown").lower()
            description = finding.get("description", "No description provided")
            location = finding.get("location", "Unknown location")
            line_number = finding.get("line_number", "")
            if line_number:
                location = f"{location}:{line_number}"
                
            snippet = finding.get("snippet", "")
            recommendation = finding.get("recommendation", "No recommendation provided")
            
            html += f"""
        <div class="finding-card">
            <div class="finding-header">
                <div class="finding-title">{finding.get("title", "Unknown Vulnerability")}</div>
                <div class="finding-severity {severity}">{severity.upper()}</div>
            </div>
            
            <div class="metadata">
                <div class="metadata-item">
                    <span class="metadata-label">ID:</span>
                    <span>{finding.get("id", "")}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Type:</span>
                    <span>{finding.get("vulnerability_type", "")}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Confidence:</span>
                    <span>{finding.get("confidence", 0.0) * 100:.0f}%</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Source:</span>
                    <span>{finding.get("source", "unknown")}</span>
                </div>
            </div>
            
            <h3>Description</h3>
            <p>{description}</p>
            
            <h3>Location</h3>
            <p>{location}</p>
            
"""

            # Add code snippet if available
            if snippet:
                html += f"""
            <h3>Code</h3>
            <pre class="code-block">{snippet}</pre>
"""

            html += f"""
            <h3>Recommendation</h3>
            <p>{recommendation}</p>
        </div>
"""

        # Finish HTML
        html += """
    </div>
</body>
</html>
"""
        return html
