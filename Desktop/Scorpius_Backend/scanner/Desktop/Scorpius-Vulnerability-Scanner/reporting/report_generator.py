"""Report Generator for Scorpius Vulnerability Scanner

This module provides functionality for generating comprehensive vulnerability
reports in various formats (JSON, HTML, PDF) from scan results.
"""

import os
import json
import logging
import datetime
from enum import Enum
from typing import List, Dict, Any, Optional, Union
from abc import ABC, abstractmethod

logger = logging.getLogger("scorpius.reporting")


class ReportFormat(Enum):
    """Supported report formats"""
    JSON = "json"
    HTML = "html"
    PDF = "pdf"
    MARKDOWN = "md"
    CSV = "csv"
    SARIF = "sarif"  # Static Analysis Results Interchange Format


class ReportGenerator(ABC):
    """Abstract base class for report generators
    
    All report format implementations should extend this class.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the report generator
        
        Args:
            config: Configuration options for the report generator
        """
        self.config = config or {}
        
    @abstractmethod
    def generate(self, scan_results: Dict[str, Any], output_path: str) -> str:
        """Generate a report from scan results
        
        Args:
            scan_results: The scan results to generate a report from
            output_path: Path to save the report to
            
        Returns:
            str: Path to the generated report
        """
        pass


class JsonReportGenerator(ReportGenerator):
    """JSON report generator
    
    Generates reports in JSON format with detailed vulnerability information.
    """
    
    def generate(self, scan_results: Dict[str, Any], output_path: str) -> str:
        """Generate a JSON report
        
        Args:
            scan_results: The scan results to generate a report from
            output_path: Path to save the report to
            
        Returns:
            str: Path to the generated report
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Add metadata to the report
        report_data = {
            "metadata": {
                "generated_at": datetime.datetime.now().isoformat(),
                "scanner_version": scan_results.get("scanner_version", "unknown"),
                "scan_duration": scan_results.get("scan_duration", 0),
                "plugins_used": scan_results.get("plugins_used", [])
            },
            "target": scan_results.get("target", {}),
            "summary": self._generate_summary(scan_results),
            "findings": scan_results.get("findings", [])
        }
        
        # Write the report to the output file
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2)
            
        logger.info(f"JSON report generated: {output_path}")
        return output_path
        
    def _generate_summary(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the scan results
        
        Args:
            scan_results: The scan results
            
        Returns:
            Dict: Summary information
        """
        findings = scan_results.get("findings", [])
        
        # Count findings by severity
        severity_counts = {}
        for finding in findings:
            severity = finding.get("severity", "unknown")
            if severity not in severity_counts:
                severity_counts[severity] = 0
            severity_counts[severity] += 1
            
        # Count findings by vulnerability type
        vuln_type_counts = {}
        for finding in findings:
            vuln_type = finding.get("vulnerability_type", "unknown")
            if vuln_type not in vuln_type_counts:
                vuln_type_counts[vuln_type] = 0
            vuln_type_counts[vuln_type] += 1
            
        return {
            "total_findings": len(findings),
            "severity_counts": severity_counts,
            "vulnerability_type_counts": vuln_type_counts,
            "scan_status": scan_results.get("status", "unknown"),
            "risk_score": self._calculate_risk_score(findings)
        }
        
    def _calculate_risk_score(self, findings: List[Dict[str, Any]]) -> float:
        """Calculate an overall risk score based on findings
        
        Args:
            findings: List of vulnerability findings
            
        Returns:
            float: Risk score from 0.0 to 10.0
        """
        if not findings:
            return 0.0
            
        # Severity weights
        weights = {
            "critical": 10.0,
            "high": 7.5,
            "medium": 5.0,
            "low": 2.5,
            "info": 0.5,
        }
        
        # Calculate weighted score
        total_score = 0.0
        for finding in findings:
            severity = finding.get("severity", "low").lower()
            confidence = finding.get("confidence", 0.5)
            weight = weights.get(severity, 1.0)
            total_score += weight * confidence
            
        # Normalize to 0-10 scale
        max_possible = len(findings) * 10.0
        if max_possible > 0:
            normalized_score = min(10.0, (total_score / max_possible) * 10.0)
        else:
            normalized_score = 0.0
            
        return round(normalized_score, 1)


class ReportingManager:
    """Manager for report generation
    
    Provides a unified interface for generating reports in various formats.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the reporting manager
        
        Args:
            config: Configuration options for reporting
        """
        self.config = config or {}
        
        # Register available report generators
        self.generators = {
            ReportFormat.JSON: JsonReportGenerator(self.config)
            # Other formats will be registered separately
        }
        
    def generate_report(self, scan_results: Dict[str, Any], output_path: str, 
                       format: Union[ReportFormat, str] = ReportFormat.JSON) -> str:
        """Generate a report
        
        Args:
            scan_results: The scan results to generate a report from
            output_path: Path to save the report to
            format: Format to generate the report in
            
        Returns:
            str: Path to the generated report
        """
        # Convert string format to enum if needed
        if isinstance(format, str):
            try:
                format = ReportFormat(format.lower())
            except ValueError:
                logger.error(f"Unknown report format: {format}")
                format = ReportFormat.JSON
                
        # Check if the format is supported
        if format not in self.generators:
            logger.warning(f"Report format {format.value} not supported, falling back to JSON")
            format = ReportFormat.JSON
            
        # Ensure the output path has the correct extension
        if not output_path.endswith(f".{format.value}"):
            output_path = f"{output_path}.{format.value}"
            
        # Generate the report
        logger.info(f"Generating {format.value} report to {output_path}")
        return self.generators[format].generate(scan_results, output_path)
    
    def register_generator(self, format: ReportFormat, generator: ReportGenerator) -> None:
        """Register a new report generator
        
        Args:
            format: Format to register the generator for
            generator: The report generator to register
        """
        self.generators[format] = generator
        logger.info(f"Registered report generator for {format.value} format")


def generate(scan_results: Dict[str, Any], output_path: str, 
            format: Union[ReportFormat, str] = ReportFormat.JSON) -> str:
    """Convenience function to generate a report
    
    Args:
        scan_results: The scan results to generate a report from
        output_path: Path to save the report to
        format: Format to generate the report in
        
    Returns:
        str: Path to the generated report
    """
    manager = ReportingManager()
    return manager.generate_report(scan_results, output_path, format)
