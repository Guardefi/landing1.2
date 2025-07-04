"""Markdown Report Generator for Scorpius Vulnerability Scanner

This module provides functionality for generating Markdown vulnerability reports
suitable for version control systems and documentation platforms.
"""

import os
import json
import logging
import datetime
from typing import Dict, Any, List

from reporting.report_generator import ReportGenerator

logger = logging.getLogger("scorpius.reporting.markdown")


class MarkdownReportGenerator(ReportGenerator):
    """Markdown report generator
    
    Generates comprehensive vulnerability reports in Markdown format.
    """
    
    def generate(self, scan_results: Dict[str, Any], output_path: str) -> str:
        """Generate a Markdown report
        
        Args:
            scan_results: The scan results to generate a report from
            output_path: Path to save the report to
            
        Returns:
            str: Path to the generated report
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Generate the Markdown content
        md_content = self._generate_markdown_content(scan_results)
        
        # Write the report to the output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
            
        logger.info(f"Markdown report generated: {output_path}")
        return output_path
    
    def _generate_markdown_content(self, scan_results: Dict[str, Any]) -> str:
        """Generate the Markdown content for the report
        
        Args:
            scan_results: The scan results
            
        Returns:
            str: Markdown content
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
        
        # Start building Markdown content
        md = f"""# Scorpius Vulnerability Report - {target_name}

## Scan Overview

- **Generated At**: {metadata['generated_at']}
- **Scanner Version**: {metadata['scanner_version']}
- **Scan Duration**: {metadata['scan_duration']} seconds
- **Scan Status**: {summary['scan_status']}
- **Risk Score**: {summary['risk_score']} / 10.0

## Plugins Used

"""

        # Add plugins used
        for plugin in metadata['plugins_used']:
            md += f"- {plugin}\n"
            
        md += """
## Summary of Findings

| Severity | Count |
|----------|-------|
"""

        # Add severity count rows
        severity_counts = summary.get("severity_counts", {})
        for severity, count in severity_counts.items():
            md += f"| **{severity.capitalize()}** | {count} |\n"
            
        md += f"\n**Total Findings**: {summary.get('total_findings', 0)}\n\n"
        
        md += """## Vulnerability Types

| Type | Count |
|------|-------|
"""

        # Add vulnerability type counts
        vuln_type_counts = summary.get("vulnerability_type_counts", {})
        for vuln_type, count in vuln_type_counts.items():
            md += f"| {vuln_type} | {count} |\n"
            
        md += "\n## Detailed Findings\n\n"
        
        # Sort findings by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        sorted_findings = sorted(
            findings, 
            key=lambda f: severity_order.get(f.get("severity", "").lower(), 999)
        )
        
        # Add detailed findings
        for i, finding in enumerate(sorted_findings, 1):
            title = finding.get("title", "Unknown Vulnerability")
            severity = finding.get("severity", "unknown").upper()
            vuln_type = finding.get("vulnerability_type", "")
            description = finding.get("description", "No description provided")
            location = finding.get("location", "Unknown location")
            line_number = finding.get("line_number", "")
            if line_number:
                location = f"{location}:{line_number}"
                
            snippet = finding.get("snippet", "")
            recommendation = finding.get("recommendation", "No recommendation provided")
            
            md += f"### {i}. {title}\n\n"
            md += f"**Severity**: {severity}  \n"
            md += f"**Type**: {vuln_type}  \n"
            md += f"**Confidence**: {finding.get('confidence', 0.0) * 100:.0f}%  \n"
            md += f"**Source**: {finding.get('source', 'unknown')}  \n"
            
            md += "\n**Description**:\n\n"
            md += f"{description}\n\n"
            
            md += "**Location**:\n\n"
            md += f"`{location}`\n\n"
            
            if snippet:
                md += "**Code**:\n\n"
                md += f"```solidity\n{snippet}\n```\n\n"
                
            md += "**Recommendation**:\n\n"
            md += f"{recommendation}\n\n"
            
            # Add CWE ID if available
            cwe_id = finding.get("cwe_id")
            if cwe_id:
                md += f"**CWE**: [CWE-{cwe_id}](https://cwe.mitre.org/data/definitions/{cwe_id}.html)\n\n"
                
            # Add tags if available
            tags = finding.get("tags", [])
            if tags:
                md += "**Tags**: " + ", ".join(f"`{tag}`" for tag in tags) + "\n\n"
                
            md += "---\n\n"
            
        return md
