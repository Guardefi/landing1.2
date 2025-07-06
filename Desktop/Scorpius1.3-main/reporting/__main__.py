"""
Scorpius Enterprise Reporting Engine
====================================

Main entry point for the enterprise reporting system.
"""

from .api import create_app
from .cli import main as cli_main
from .core import ReportEngine, ReportBuilder, ReportExporter
from .generator import ReportGenerator
from .models import ReportJob, ReportTemplate, ScanResult, VulnerabilityFinding
from .themes import ThemeManager, ThemeType
from .widgets import WidgetRegistry

__version__ = "1.0.0"
__author__ = "Scorpius Security"

# Main exports
__all__ = [
    "ReportEngine",
    "ReportBuilder", 
    "ReportExporter",
    "ReportGenerator",
    "ReportJob",
    "ReportTemplate",
    "ScanResult",
    "VulnerabilityFinding",
    "ThemeManager",
    "ThemeType",
    "WidgetRegistry",
    "create_app",
    "cli_main",
]


def get_version() -> str:
    """Get the version string"""
    return __version__


def create_sample_report():
    """Create a sample report for testing"""
    import asyncio
    
    async def _create_sample():
        generator = ReportGenerator()
        sample_scan = generator.create_sample_scan_result()
        
        print("Generating sample reports...")
        report_files = await generator.generate_full_audit_report(
            sample_scan, 
            formats=["html", "json"]
        )
        
        print("Sample reports generated:")
        for format_name, file_path in report_files.items():
            print(f"  {format_name.upper()}: {file_path}")
        
        return report_files
    
    return asyncio.run(_create_sample())


if __name__ == "__main__":
    # If run as a module, start CLI
    cli_main()
