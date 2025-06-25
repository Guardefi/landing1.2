"""
CSV Report Writer
=================

Generate CSV reports for spreadsheet applications and data analysis.
"""

import csv
from io import StringIO
from pathlib import Path
from typing import Dict, Optional

from .base import BaseReporter, ReportContext


class CSVReporter(BaseReporter):
    """CSV report generator for tabular data export"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        super().__init__(output_dir)
        self.supported_formats = ["csv"]
        
    async def generate(
        self,
        context: ReportContext,
        output_path: Optional[Path] = None,
        include_summary: bool = True,
        include_scan_details: bool = True,
        delimiter: str = ",",
        encoding: str = "utf-8-sig",  # Excel-friendly encoding
        **kwargs
    ) -> Path:
        """
        Generate CSV report.
        
        Args:
            context: Report context with scan data
            output_path: Optional custom output path
            include_summary: Whether to include summary sheet
            include_scan_details: Whether to include scan details sheet
            delimiter: CSV delimiter character
            encoding: File encoding
            **kwargs: Additional options
            
        Returns:
            Path to generated CSV file
        """
        # Validate context
        errors = await self.validate_context(context)
        if errors:
            raise ValueError(f"Context validation failed: {'; '.join(errors)}")
            
        # Prepare output path
        if not output_path:
            filename = self.get_default_filename(context)
            output_path = self.output_dir / filename
            
        # Generate CSV content
        csv_content = self._generate_csv_content(
            context, include_summary, include_scan_details, delimiter
        )
        
        # Write CSV file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', newline='', encoding=encoding) as f:
            f.write(csv_content)
            
        return output_path
        
    def _generate_csv_content(
        self,
        context: ReportContext,
        include_summary: bool,
        include_scan_details: bool,
        delimiter: str
    ) -> str:
        """Generate the complete CSV content"""
        
        output = StringIO()
        
        # Write vulnerabilities (main data)
        self._write_vulnerabilities_section(output, context, delimiter)
        
        if include_summary:
            output.write("\n\n")
            self._write_summary_section(output, context, delimiter)
            
        if include_scan_details:
            output.write("\n\n")
            self._write_scan_details_section(output, context, delimiter)
            
        return output.getvalue()
        
    def _write_vulnerabilities_section(
        self, 
        output: StringIO, 
        context: ReportContext, 
        delimiter: str
    ) -> None:
        """Write vulnerabilities data to CSV"""
        
        writer = csv.writer(output, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
        
        # Header comment
        writer.writerow(["# VULNERABILITIES"])
        writer.writerow([])
        
        # Column headers
        headers = [
            "Project",
            "Vulnerability ID",
            "Title",
            "Description",
            "Severity",
            "Category",
            "Risk Score",
            "Confidence",
            "Function",
            "Contract",
            "Line Number",
            "Impact",
            "Recommendation",
            "Tool",
            "Rule ID",
            "CWE ID",
            "References",
            "Scan Date",
        ]
        writer.writerow(headers)
        
        # Data rows
        for scan in context.scan_results:
            for vuln in scan.vulnerabilities:
                row = [
                    scan.project_name,
                    vuln.id,
                    vuln.title,
                    vuln.description,
                    vuln.severity.value,
                    vuln.category.value,
                    f"{vuln.risk_score:.2f}",
                    f"{vuln.confidence:.2f}",
                    vuln.function_name or "",
                    vuln.contract_name or "",
                    vuln.line_number or "",
                    vuln.impact or "",
                    vuln.recommendation or "",
                    vuln.tool_name or "",
                    vuln.rule_id or "",
                    vuln.cwe_id or "",
                    "; ".join(vuln.references) if vuln.references else "",
                    scan.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                ]
                writer.writerow(row)
                
    def _write_summary_section(
        self, 
        output: StringIO, 
        context: ReportContext, 
        delimiter: str
    ) -> None:
        """Write summary statistics to CSV"""
        
        writer = csv.writer(output, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
        
        # Header comment
        writer.writerow(["# SUMMARY STATISTICS"])
        writer.writerow([])
        
        stats = context.get_aggregated_stats()
        
        # Summary table
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Scans", stats.get("total_scans", 0)])
        writer.writerow(["Total Contracts", stats.get("total_contracts", 0)])
        writer.writerow(["Total Vulnerabilities", stats.get("total_issues", 0)])
        writer.writerow(["Critical Issues", stats.get("critical_issues", 0)])
        writer.writerow(["High Issues", stats.get("high_issues", 0)])
        writer.writerow(["Medium Issues", stats.get("medium_issues", 0)])
        writer.writerow(["Low Issues", stats.get("low_issues", 0)])
        writer.writerow(["Info Issues", stats.get("info_issues", 0)])
        
        # Risk assessment by project
        writer.writerow([])
        writer.writerow(["# RISK ASSESSMENT BY PROJECT"])
        writer.writerow([])
        writer.writerow(["Project", "Risk Level", "Risk Score", "Total Issues", "Critical", "High", "Medium", "Low"])
        
        for scan in context.scan_results:
            risk_summary = scan.get_risk_summary()
            writer.writerow([
                scan.project_name,
                risk_summary["overall_risk"],
                f"{risk_summary['risk_score']:.2f}",
                scan.total_issues,
                scan.critical_issues,
                scan.high_issues,
                scan.medium_issues,
                scan.low_issues,
            ])
            
    def _write_scan_details_section(
        self, 
        output: StringIO, 
        context: ReportContext, 
        delimiter: str
    ) -> None:
        """Write scan details to CSV"""
        
        writer = csv.writer(output, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
        
        # Header comment
        writer.writerow(["# SCAN DETAILS"])
        writer.writerow([])
        
        # Headers
        headers = [
            "Scan ID",
            "Project Name",
            "Project Version",
            "Status",
            "Created At",
            "Completed At",
            "Duration (seconds)",
            "Contracts Count",
            "Total Issues",
            "Critical",
            "High", 
            "Medium",
            "Low",
            "Info",
        ]
        writer.writerow(headers)
        
        # Data rows
        for scan in context.scan_results:
            duration = ""
            if scan.metrics and scan.metrics.duration_seconds:
                duration = f"{scan.metrics.duration_seconds:.2f}"
            elif scan.completed_at and scan.started_at:
                duration = f"{(scan.completed_at - scan.started_at).total_seconds():.2f}"
                
            row = [
                scan.id,
                scan.project_name,
                scan.project_version or "",
                scan.status.value,
                scan.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                scan.completed_at.strftime("%Y-%m-%d %H:%M:%S") if scan.completed_at else "",
                duration,
                len(scan.contracts),
                scan.total_issues,
                scan.critical_issues,
                scan.high_issues,
                scan.medium_issues,
                scan.low_issues,
                scan.info_issues,
            ]
            writer.writerow(row)
            
    def get_file_extension(self) -> str:
        """Get file extension for CSV reports"""
        return "csv"


class VulnerabilityCSVReporter(CSVReporter):
    """Specialized CSV reporter for vulnerability data only"""
    
    async def generate(
        self,
        context: ReportContext,
        output_path: Optional[Path] = None,
        **kwargs
    ) -> Path:
        """Generate CSV with vulnerabilities only"""
        
        kwargs.update({
            "include_summary": False,
            "include_scan_details": False,
        })
        
        return await super().generate(context, output_path, **kwargs)


class SummaryCSVReporter(CSVReporter):
    """Specialized CSV reporter for summary data only"""
    
    def _generate_csv_content(
        self,
        context: ReportContext,
        include_summary: bool,
        include_scan_details: bool,
        delimiter: str
    ) -> str:
        """Generate summary-only CSV content"""
        
        output = StringIO()
        self._write_summary_section(output, context, delimiter)
        return output.getvalue()


class PivotCSVReporter(CSVReporter):
    """CSV reporter optimized for pivot table analysis"""
    
    def _write_vulnerabilities_section(
        self, 
        output: StringIO, 
        context: ReportContext, 
        delimiter: str
    ) -> None:
        """Write vulnerabilities in pivot-friendly format"""
        
        writer = csv.writer(output, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
        
        # Headers optimized for pivot analysis
        headers = [
            "Date",
            "Project",
            "Severity",
            "Category", 
            "Risk_Score_Range",
            "Function_Name",
            "Contract_Name",
            "Tool_Name",
            "Count",  # Always 1 for individual vulnerabilities
            "Risk_Score",
            "Confidence",
            "Title",
            "Description",
        ]
        writer.writerow(headers)
        
        # Data rows
        for scan in context.scan_results:
            scan_date = scan.created_at.strftime("%Y-%m-%d")
            
            for vuln in scan.vulnerabilities:
                risk_range = self._get_risk_score_range(vuln.risk_score)
                
                row = [
                    scan_date,
                    scan.project_name,
                    vuln.severity.value,
                    vuln.category.value,
                    risk_range,
                    vuln.function_name or "N/A",
                    vuln.contract_name or "N/A",
                    vuln.tool_name or "N/A",
                    1,  # Count
                    f"{vuln.risk_score:.2f}",
                    f"{vuln.confidence:.2f}",
                    vuln.title,
                    vuln.description,
                ]
                writer.writerow(row)
                
    def _get_risk_score_range(self, risk_score: float) -> str:
        """Get risk score range for pivot analysis"""
        if risk_score >= 8.0:
            return "8.0-10.0"
        elif risk_score >= 6.0:
            return "6.0-7.9"
        elif risk_score >= 4.0:
            return "4.0-5.9"
        elif risk_score >= 2.0:
            return "2.0-3.9"
        else:
            return "0.0-1.9"


class MultiSheetCSVExporter:
    """Export multiple CSV sheets as separate files"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def export_all_sheets(
        self,
        context: ReportContext,
        base_filename: str,
        delimiter: str = ",",
        encoding: str = "utf-8-sig"
    ) -> Dict[str, Path]:
        """
        Export all data as separate CSV files.
        
        Args:
            context: Report context
            base_filename: Base filename (without extension)
            delimiter: CSV delimiter
            encoding: File encoding
            
        Returns:
            Dictionary mapping sheet names to file paths
        """
        
        files = {}
        
        # Vulnerabilities sheet
        vuln_reporter = VulnerabilityCSVReporter(self.output_dir)
        vuln_path = await vuln_reporter.generate(
            context,
            self.output_dir / f"{base_filename}_vulnerabilities.csv",
            delimiter=delimiter,
            encoding=encoding
        )
        files["vulnerabilities"] = vuln_path
        
        # Summary sheet
        summary_reporter = SummaryCSVReporter(self.output_dir)
        summary_path = await summary_reporter.generate(
            context,
            self.output_dir / f"{base_filename}_summary.csv",
            delimiter=delimiter,
            encoding=encoding
        )
        files["summary"] = summary_path
        
        # Pivot data sheet
        pivot_reporter = PivotCSVReporter(self.output_dir)
        pivot_path = await pivot_reporter.generate(
            context,
            self.output_dir / f"{base_filename}_pivot.csv",
            delimiter=delimiter,
            encoding=encoding
        )
        files["pivot"] = pivot_path
        
        return files

