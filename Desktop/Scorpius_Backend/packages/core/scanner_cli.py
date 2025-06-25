"""
Enhanced Command Line Interface for Scorpius Vulnerability Scanner
Provides a comprehensive CLI with advanced analysis capabilities
"""
import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.syntax import Syntax
from rich import box
from rich.text import Text

from core.engine import ScanEngine
from core.models import (
    ScanType, Target, ScanConfig, VulnerabilityLevel
)
from ai.vulnerability_analyzer import EnhancedVulnerabilityAnalyzer
from reporting import ReportFormat
from utils.logging_utils import setup_logger

# Set up logger and console
logger = setup_logger("scorpius.cli", log_level=logging.INFO)
console = Console()

class ScannerCLI:
    """Command-line interface for Scorpius Vulnerability Scanner"""
    
    def __init__(self):
        """Initialize the CLI parser"""
        self.parser = self._create_parser()
        self.engine = None
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser with all options"""
        parser = argparse.ArgumentParser(
            description="Scorpius Enterprise-Grade Smart Contract Vulnerability Scanner",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # Create subparsers for different commands
        subparsers = parser.add_subparsers(dest="command", help="Command to execute")
        
        # Scan command
        scan_parser = subparsers.add_parser("scan", help="Run a vulnerability scan")
        scan_parser.add_argument(
            "--target", "-t", required=True,
            help="Target to scan: file path, directory, contract address, or URL"
        )
        scan_parser.add_argument(
            "--scan-type", "-s", choices=["static", "dynamic", "deployed", "comprehensive"],
            default="comprehensive", 
            help="Type of scan to perform"
        )
        scan_parser.add_argument(
            "--config", "-c", 
            help="Path to scan configuration file (JSON)"
        )
        scan_parser.add_argument(
            "--output-dir", "-o", 
            help="Directory for scan results"
        )
        scan_parser.add_argument(
            "--report-formats", "-r", nargs="+", choices=["json", "html", "markdown"],
            default=["json"],
            help="Report formats to generate"
        )
        scan_parser.add_argument(
            "--plugins", "-p", nargs="+",
            help="Specific plugins to use for scanning"
        )
        scan_parser.add_argument(
            "--exclude-plugins", "-e", nargs="+",
            help="Plugins to exclude from scanning"
        )
        scan_parser.add_argument(
            "--sandbox", action="store_true", default=True,
            help="Run in sandbox mode (default: True)"
        )
        scan_parser.add_argument(
            "--no-sandbox", action="store_false", dest="sandbox",
            help="Disable sandbox mode"
        )
        scan_parser.add_argument(
            "--verbosity", "-v", choices=["debug", "info", "warning", "error"],
            default="info",
            help="Logging verbosity"
        )
        scan_parser.add_argument(
            "--wait", "-w", action="store_true", default=True,
            help="Wait for scan completion and show results"
        )
        
        # Status command
        status_parser = subparsers.add_parser("status", help="Check status of a scan")
        status_parser.add_argument(
            "--scan-id", "-i", required=True,
            help="ID of the scan to check"
        )
        
        # List command for plugins
        list_parser = subparsers.add_parser("list", help="List available plugins")
        list_parser.add_argument(
            "--types", "-t", action="store_true",
            help="List available scan types"
        )
        list_parser.add_argument(
            "--report-formats", "-r", action="store_true",
            help="List available report formats"
        )
        
        return parser
    
    async def _initialize_engine(self, config_path: str = None) -> None:
        """Initialize the scan engine if not already done"""
        if not self.engine:
            self.engine = ScanEngine(config_path=config_path)
    
    def _parse_scan_config(self, args: argparse.Namespace) -> ScanConfig:
        """
        Parse command-line arguments into a ScanConfig object
        
        Args:
            args: Command-line arguments
            
        Returns:
            ScanConfig: Parsed scan configuration
        """
        config = ScanConfig()
        
        # Set report formats
        report_formats = []
        for fmt in args.report_formats:
            if fmt.upper() in ReportFormat.__members__:
                report_formats.append(fmt.upper())
        config.report_formats = report_formats
        
        # Set generate reports flag
        config.generate_reports = True
        
        # Set plugins
        if args.plugins:
            config.enabled_plugins = args.plugins
        if args.exclude_plugins:
            config.disabled_plugins = args.exclude_plugins
        
        # Read from config file if provided
        if args.config:
            try:
                with open(args.config, 'r') as f:
                    config_data = json.load(f)
                    
                # Update config with file values
                for key, value in config_data.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
            except Exception as e:
                logger.error(f"Error loading config file: {e}")
        
        # Add custom options
        config.custom_options = {
            "output_dir": args.output_dir if args.output_dir else "reports",
            "sandbox_enabled": args.sandbox
        }
        
        return config
    
    def _parse_target(self, target_spec: str) -> Target:
        """
        Parse a target specification string into a Target object
        
        Args:
            target_spec: Target specification string
            
        Returns:
            Target: Parsed target
        """
        target = Target()
        
        # Check if it's a file or directory
        if os.path.exists(target_spec):
            # Resolve path to absolute
            absolute_path = os.path.abspath(target_spec)
            
            if os.path.isfile(absolute_path):
                target.source_files = [absolute_path]
                target.target_type = "source_file"
                target.identifier = os.path.basename(absolute_path)
            elif os.path.isdir(absolute_path):
                target.source_dir = absolute_path
                target.target_type = "source_dir"
                target.identifier = os.path.basename(absolute_path)
        # Check if it's an Ethereum address
        elif target_spec.startswith("0x") and len(target_spec) == 42:
            target.contract_address = target_spec
            target.target_type = "deployed_contract"
            target.identifier = target_spec
        # Otherwise assume it's a URL
        else:
            target.contract_url = target_spec
            target.target_type = "contract_url"
            target.identifier = target_spec
        
        return target
    
    def _parse_scan_type(self, scan_type_str: str) -> ScanType:
        """
        Parse a scan type string into a ScanType enum
        
        Args:
            scan_type_str: Scan type string
            
        Returns:
            ScanType: Parsed scan type enum
        """
        scan_type_map = {
            "static": ScanType.STATIC,
            "dynamic": ScanType.DYNAMIC,
            "deployed": ScanType.DEPLOYED,
            "comprehensive": ScanType.COMPREHENSIVE
        }
        
        return scan_type_map.get(scan_type_str.lower(), ScanType.COMPREHENSIVE)
    
    async def execute(self, args: Optional[List[str]] = None) -> None:
        """
        Execute the CLI with the given arguments
        
        Args:
            args: Command-line arguments, defaults to sys.argv
        """
        # Parse arguments
        args = self.parser.parse_args(args)
        
        # Configure logging
        if hasattr(args, 'verbosity'):
            log_level = getattr(logging, args.verbosity.upper())
            logger.setLevel(log_level)
        
        # Initialize engine
        await self._initialize_engine()
        
        # Execute the appropriate command
        if args.command == "scan":
            await self._handle_scan_command(args)
        elif args.command == "status":
            await self._handle_status_command(args)
        elif args.command == "list":
            await self._handle_list_command(args)
        else:
            self.parser.print_help()
    
    async def _handle_scan_command(self, args: argparse.Namespace) -> None:
        """
        Handle the scan command
        
        Args:
            args: Command-line arguments
        """
        # Parse target
        target = self._parse_target(args.target)
        
        # Parse scan type
        scan_type = self._parse_scan_type(args.scan_type)
        
        # Parse config
        config = self._parse_scan_config(args)
        
        # Start the scan
        scan_id = await self.engine.start_scan(target, scan_type, config)
        print(f"Scan started with ID: {scan_id}")
        
        # Wait for completion if requested
        if args.wait:
            print("Waiting for scan to complete...")
            completed = False
            
            while not completed:
                scan_result = await self.engine.get_scan_status(scan_id)
                
                # Check if completed or failed
                if scan_result.status.name in ["COMPLETED", "FAILED", "CANCELLED"]:
                    completed = True
                    print(f"Scan {scan_result.status.name.lower()}")
                    
                    if scan_result.status.name == "COMPLETED":
                        # Print summary of findings
                        severity_counts = {}
                        for finding in scan_result.findings:
                            severity = finding.severity.name
                            if severity not in severity_counts:
                                severity_counts[severity] = 0
                            severity_counts[severity] += 1
                        
                        print("\nScan Results Summary:")
                        print("=" * 30)
                        total_findings = len(scan_result.findings)
                        print(f"Total findings: {total_findings}")
                        
                        for severity in VulnerabilityLevel:
                            count = severity_counts.get(severity.name, 0)
                            print(f"{severity.name}: {count}")
                        
                        print("\nReports generated:")
                        for report_format in config.report_formats:
                            report_path = f"{config.custom_options['output_dir']}/scan-{scan_id[:8]}"
                            print(f" - {report_path}.{report_format.lower()}")
                    
                    elif scan_result.status.name == "FAILED":
                        print(f"Scan failed with error: {scan_result.error}")
                else:
                    # Print progress and sleep
                    if hasattr(scan_result, 'progress') and scan_result.progress is not None:
                        print(f"Progress: {scan_result.progress}%", end="\r")
                    await asyncio.sleep(1)
    
    async def _handle_status_command(self, args: argparse.Namespace) -> None:
        """
        Handle the status command
        
        Args:
            args: Command-line arguments
        """
        scan_result = await self.engine.get_scan_status(args.scan_id)
        
        if not scan_result:
            print(f"No scan found with ID: {args.scan_id}")
            return
        
        print(f"Scan ID: {args.scan_id}")
        print(f"Status: {scan_result.status.name}")
        print(f"Target: {scan_result.target.identifier}")
        print(f"Scan Type: {scan_result.scan_type.name}")
        print(f"Start Time: {scan_result.start_time}")
        
        if scan_result.end_time:
            print(f"End Time: {scan_result.end_time}")
        
        if hasattr(scan_result, 'progress') and scan_result.progress is not None:
            print(f"Progress: {scan_result.progress}%")
        
        if scan_result.status.name == "COMPLETED":
            print(f"Findings: {len(scan_result.findings)}")
    
    async def _handle_list_command(self, args: argparse.Namespace) -> None:
        """
        Handle the list command
        
        Args:
            args: Command-line arguments
        """
        if args.types:
            print("Available scan types:")
            for scan_type in ScanType:
                print(f" - {scan_type.name.lower()}")
        
        elif args.report_formats:
            print("Available report formats:")
            for report_format in ReportFormat:
                print(f" - {report_format.name.lower()}")
        
        else:
            # List plugins
            plugins = self.engine.plugin_manager.get_plugins()
            
            print("Available plugins:")
            for name, plugin in plugins.items():
                scan_types = [t.name for t in plugin.SUPPORTED_SCAN_TYPES]
                print(f" - {name} v{plugin.VERSION}")
                print(f"   Description: {plugin.DESCRIPTION}")
                print(f"   Author: {plugin.AUTHOR}")
                print(f"   Supported Scan Types: {', '.join(scan_types)}")
                print()

def main():
    """Main entry point for the CLI"""
    cli = ScannerCLI()
    asyncio.run(cli.execute())

if __name__ == "__main__":
    main()
