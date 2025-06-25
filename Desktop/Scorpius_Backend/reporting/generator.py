"""
Report Generator Utilities
==========================

High-level utilities for generating complete reports with all formats and features.
"""

import asyncio
import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Dict, List

from diff_engine import ReportDiffEngine
from models import ScanResult, VulnerabilityFinding, SeverityLevel, VulnerabilityCategory, FindingType
from reporters import (
    CSVReporter,
    HTMLReporter,
    JSONReporter,
    MarkdownReporter,
    PDFReporter,
    SARIFReporter,
)
from reporters.base import ReportContext, ReportMetadata
from themes import ThemeManager


class ReportGenerator:
    """
    High-level report generator that coordinates all report formats and features.
    """

    def __init__(
        self,
        output_dir: str = "reports",
        theme_manager: ThemeManager | None = None,
    ):
        """
        Initialize report generator.

        Args:
            output_dir: Output directory for reports
            theme_manager: Theme manager instance
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.theme_manager = theme_manager or ThemeManager()

        # Initialize report writers
        self.writers = {
            "html": HTMLReporter(),
            "pdf": PDFReporter(),
            "json": JSONReporter(),
            "csv": CSVReporter(),
            "markdown": MarkdownReporter(),
            "sarif": SARIFReporter(),
        }

    async def generate_full_audit_report(
        self,
        scan_result: ScanResult,
        formats: List[str] | None = None,
        theme: str = "Light Corporate",
        include_signature: bool = False,
    ) -> Dict[str, Path]:
        """
        Generate a complete audit report in multiple formats.

        Args:
            scan_result: Scan result data
            formats: List of formats to generate (default: all)
            theme: Theme to use
            include_signature: Whether to include digital signature

        Returns:
            Dictionary mapping format names to output file paths
        """
        if formats is None:
            formats = ["html", "pdf", "json", "csv", "sarif"]

        # Get theme configuration
        theme_config = self.theme_manager.get_theme(theme)
        theme_css = self.theme_manager.generate_css_for_theme(theme)

        # Create report metadata
        metadata = ReportMetadata(
            title=f"Security Audit Report - {scan_result.project_name}",
            description=f"Comprehensive security audit report for {scan_result.project_name}",
            author="Scorpius Security Scanner",
            created_at=datetime.now(UTC),
            version="1.0.0",
            template="audit_report"
        )

        # Prepare report context - note that scan_result is a single result, but ReportContext expects a list
        context = ReportContext(
            scan_results=[scan_result],  # Wrap single scan in a list
            metadata=metadata,
            config={
                "theme": theme,
                "include_signature": include_signature,
            },
            template_vars={
                "theme_css": theme_css,
                "scanner_version": "1.0.0",
                "total_lines": getattr(scan_result, "total_lines", 0),
            }
        )

        output_files = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Generate each requested format
        for format_name in formats:
            if format_name not in self.writers:
                continue

            writer = self.writers[format_name]
            filename = f"security_audit_{scan_result.project_name}_{timestamp}.{format_name}"
            output_path = self.output_dir / filename

            try:
                # Generate report - reporters create their own files and return paths
                generated_path = await writer.generate(context, output_path)
                output_files[format_name] = generated_path

            except Exception as e:
                print(f"Error generating {format_name} report: {e}")
                continue

        return output_files

    async def generate_diff_report(
        self,
        baseline_scan: ScanResult,
        current_scan: ScanResult,
        output_format: str = "html",
    ) -> Path:
        """
        Generate a diff report comparing two scans.

        Args:
            baseline_scan: Baseline scan result
            current_scan: Current scan result  
            output_format: Output format

        Returns:
            Path to generated diff report
        """
        # Generate diff using diff engine
        diff_engine = ReportDiffEngine()
        diff_result = diff_engine.compare_scans(baseline_scan, current_scan)

        # Prepare context for diff report
        metadata = ReportMetadata(
            title=f"Scan Comparison Report - {current_scan.project_name}",
            description=f"Comparison between baseline and current scan for {current_scan.project_name}",
            author="Scorpius Security Scanner",
            created_at=datetime.now(UTC),
            version="1.0.0",
            template="diff_report"
        )

        context = ReportContext(
            scan_results=[baseline_scan, current_scan],
            metadata=metadata,
            config={
                "diff_result": diff_result,
                "comparison_mode": True,
            },
            template_vars={
                "baseline_scan": baseline_scan,
                "current_scan": current_scan,
                "diff_result": diff_result,
            }
        )

        # Generate report
        writer = self.writers.get(output_format, self.writers["html"])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"diff_report_{current_scan.project_name}_{timestamp}.{output_format}"
        output_path = self.output_dir / filename

        generated_path = await writer.generate(context, output_path)
        return generated_path

    async def create_audit_bundle(
        self,
        scan_result: ScanResult,
        include_formats: List[str] | None = None,
        include_source: bool = True,
    ) -> Path:
        """
        Create a complete audit bundle with all reports and supporting files.

        Args:
            scan_result: Scan result data
            include_formats: Formats to include in bundle
            include_source: Whether to include source code

        Returns:
            Path to generated zip bundle
        """
        if include_formats is None:
            include_formats = ["html", "pdf", "json", "csv", "sarif"]

        # Generate all reports
        report_files = await self.generate_full_audit_report(
            scan_result, formats=include_formats
        )

        # Create bundle
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bundle_name = f"audit_bundle_{scan_result.project_name}_{timestamp}.zip"
        bundle_path = self.output_dir / bundle_name

        with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as bundle:
            # Add all report files
            for format_name, file_path in report_files.items():
                bundle.write(file_path, f"reports/{file_path.name}")

            # Add metadata
            metadata = {
                "bundle_created": datetime.now(UTC).isoformat(),
                "project_name": scan_result.project_name,
                "scan_id": scan_result.scan_id,
                "total_vulnerabilities": len(scan_result.findings),
                "formats_included": list(report_files.keys()),
                "generator_version": "1.0.0",
            }

            bundle.writestr("metadata.json", json.dumps(metadata, indent=2))

            # Add source code if requested
            if include_source and hasattr(scan_result, "source_files"):
                for source_file in getattr(scan_result, "source_files", []):
                    if Path(source_file).exists():
                        bundle.write(source_file, f"source/{Path(source_file).name}")

            # Add scan result data
            scan_data = scan_result.model_dump() if hasattr(scan_result, "model_dump") else scan_result.__dict__
            bundle.writestr(
                "scan_result.json",
                json.dumps(scan_data, indent=2, default=str)
            )

        return bundle_path

    def create_sample_scan_result(self) -> ScanResult:
        """
        Create a sample scan result for testing and demonstration.

        Returns:
            Sample ScanResult object
        """
        sample_findings = [
            VulnerabilityFinding(
                id="VULN-001",
                title="Reentrancy Vulnerability",
                description="Function allows reentrancy attacks through external calls",
                severity=SeverityLevel.CRITICAL,
                category=VulnerabilityCategory.REENTRANCY,
                type=FindingType.REENTRANCY,
                confidence=0.9,
                contract_name="TokenContract",
                function_name="withdraw",
                line_number=45,
                code_snippet="function withdraw() public {\n    (bool success,) = msg.sender.call{value: balance[msg.sender]}(\"\");\n    balance[msg.sender] = 0;\n}",
                impact="Attacker could drain contract funds",
                recommendation="Use checks-effects-interactions pattern",
                risk_score=9.5,
            ),
            VulnerabilityFinding(
                id="VULN-002", 
                title="Integer Overflow",
                description="Arithmetic operation could overflow",
                severity=SeverityLevel.HIGH,
                category=VulnerabilityCategory.ARITHMETIC,
                type=FindingType.ARITHMETIC_ISSUES,
                confidence=0.8,
                contract_name="TokenContract",
                function_name="transfer",
                line_number=23,
                code_snippet="balance[to] += amount;",
                impact="Could lead to incorrect balance calculations",
                recommendation="Use SafeMath library or Solidity 0.8+ built-in checks",
                risk_score=7.8,
            ),
            VulnerabilityFinding(
                id="VULN-003",
                title="Missing Access Control",
                description="Administrative function lacks proper access control",
                severity=SeverityLevel.MEDIUM,
                category=VulnerabilityCategory.ACCESS_CONTROL,
                type=FindingType.ACCESS_CONTROL,
                confidence=0.9,
                contract_name="TokenContract",
                function_name="setOwner",
                line_number=67,
                code_snippet="function setOwner(address newOwner) public {\n    owner = newOwner;\n}",
                impact="Unauthorized users could take control",
                recommendation="Add onlyOwner modifier",
                risk_score=5.2,
            ),
        ]

        return ScanResult(
            scan_id="SCAN-2024-001",
            project_name="TokenContract",
            project_version="1.0.0",
            vulnerabilities=sample_findings,
            metadata={
                "scanner_version": "1.0.0",
                "scan_duration": 45.2,
                "total_lines": 256,
                "solidity_version": "0.8.19",
            },
        )


async def main():
    """Demo function to test the report generator"""
    generator = ReportGenerator()
    
    # Create sample data
    sample_scan = generator.create_sample_scan_result()
    
    # Generate reports
    print("Generating audit reports...")
    report_files = await generator.generate_full_audit_report(sample_scan)
    
    print("Generated reports:")
    for format_name, file_path in report_files.items():
        print(f"  {format_name.upper()}: {file_path}")
    
    # Create audit bundle
    print("\nCreating audit bundle...")
    bundle_path = await generator.create_audit_bundle(sample_scan)
    print(f"Audit bundle: {bundle_path}")


if __name__ == "__main__":
    asyncio.run(main())

