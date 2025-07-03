"""
Command Line Interface for Scorpius Reporting Engine
===================================================

CLI tool for generating reports from scan results.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from generator import ReportGenerator
from models import ScanResult


async def generate_reports_command(args) -> None:
    """Generate reports from scan results"""
    try:
        # Load scan result data
        if args.scan_file:
            with open(args.scan_file, "r", encoding="utf-8") as f:
                scan_data = json.load(f)
            
            # Convert to ScanResult object
            scan_result = ScanResult.model_validate(scan_data)
        else:
            # Use sample data for demo
            generator = ReportGenerator(output_dir=args.output_dir)
            scan_result = generator.create_sample_scan_result()

        # Initialize generator
        generator = ReportGenerator(output_dir=args.output_dir)

        # Determine formats
        formats = args.formats.split(",") if args.formats else ["html", "pdf", "json"]
        formats = [f.strip() for f in formats]

        print(f"Generating reports for project: {scan_result.project_name}")
        print(f"Output directory: {args.output_dir}")
        print(f"Formats: {', '.join(formats)}")

        # Generate reports
        report_files = await generator.generate_full_audit_report(
            scan_result=scan_result,
            formats=formats,
            theme=args.theme,
            include_signature=args.sign,
        )

        print("\nGenerated reports:")
        for format_name, file_path in report_files.items():
            print(f"  {format_name.upper()}: {file_path}")

        # Create bundle if requested
        if args.bundle:
            print("\nCreating audit bundle...")
            bundle_path = await generator.create_audit_bundle(
                scan_result=scan_result,
                include_formats=formats,
                include_source=args.include_source,
            )
            print(f"Audit bundle: {bundle_path}")

    except Exception as e:
        print(f"Error generating reports: {e}")
        sys.exit(1)


async def diff_command(args) -> None:
    """Generate diff report between two scans"""
    try:
        # Load scan results
        with open(args.baseline, "r", encoding="utf-8") as f:
            baseline_data = json.load(f)
        baseline_scan = ScanResult.model_validate(baseline_data)

        with open(args.current, "r", encoding="utf-8") as f:
            current_data = json.load(f)
        current_scan = ScanResult.model_validate(current_data)

        # Generate diff report
        generator = ReportGenerator(output_dir=args.output_dir)
        
        print("Comparing scans:")
        print(f"  Baseline: {baseline_scan.scan_id}")
        print(f"  Current:  {current_scan.scan_id}")

        diff_report_path = await generator.generate_diff_report(
            baseline_scan=baseline_scan,
            current_scan=current_scan,
            output_format=args.format,
        )

        print(f"\nDiff report generated: {diff_report_path}")

    except Exception as e:
        print(f"Error generating diff report: {e}")
        sys.exit(1)


def list_themes_command(args) -> None:
    """List available themes"""
    from themes import ThemeManager
    
    theme_manager = ThemeManager()
    themes = theme_manager.list_themes()
    
    print("Available themes:")
    for theme in themes:
        if isinstance(theme, dict):
            print(f"  {theme['name']:<20} - {theme['description']}")
        else:
            # theme is a string name, get details from theme manager
            theme_details = theme_manager.get_theme(theme)
            description = theme_details.description if hasattr(theme_details, 'description') else 'No description available'
            display_name = theme_details.display_name if hasattr(theme_details, 'display_name') else theme
            print(f"  {display_name:<20} - {description}")


def validate_scan_command(args) -> None:
    """Validate scan result file format"""
    try:
        with open(args.scan_file, "r", encoding="utf-8") as f:
            scan_data = json.load(f)
        
        # Try to validate as ScanResult
        scan_result = ScanResult.model_validate(scan_data)
        
        print("✓ Scan file is valid")
        print(f"  Project: {scan_result.project_name}")
        print(f"  Scan ID: {scan_result.scan_id}")
        print(f"  Findings: {len(scan_result.findings)}")
        
    except Exception as e:
        print(f"✗ Scan file validation failed: {e}")
        sys.exit(1)


def create_sample_command(args) -> None:
    """Create sample scan result file"""
    generator = ReportGenerator()
    sample_scan = generator.create_sample_scan_result()
    
    output_path = Path(args.output) if args.output else Path("sample_scan.json")
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            sample_scan.model_dump() if hasattr(sample_scan, "model_dump") else sample_scan.__dict__,
            f,
            indent=2,
            default=str
        )
    
    print(f"Sample scan result created: {output_path}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Scorpius Security Report Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate reports from scan file
  python -m reporting.cli generate --scan-file scan_results.json --formats html,pdf
  
  # Generate sample reports
  python -m reporting.cli generate --formats html,json --theme "Dark Pro"
  
  # Create audit bundle
  python -m reporting.cli generate --bundle --include-source
  
  # Compare two scans
  python -m reporting.cli diff baseline.json current.json
  
  # List available themes
  python -m reporting.cli themes
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate audit reports")
    generate_parser.add_argument(
        "--scan-file", 
        "-s", 
        type=str,
        help="JSON file containing scan results (uses sample data if not provided)"
    )
    generate_parser.add_argument(
        "--output-dir", 
        "-o", 
        type=str, 
        default="reports",
        help="Output directory for reports (default: reports)"
    )
    generate_parser.add_argument(
        "--formats", 
        "-f", 
        type=str,
        default="html,pdf,json",
        help="Comma-separated list of formats (html,pdf,json,csv,sarif,markdown)"
    )
    generate_parser.add_argument(
        "--theme", 
        "-t", 
        type=str, 
        default="Light Corporate",
        help="Theme to use for reports"
    )
    generate_parser.add_argument(
        "--bundle", 
        "-b", 
        action="store_true",
        help="Create audit bundle zip file"
    )
    generate_parser.add_argument(
        "--include-source", 
        action="store_true",
        help="Include source code in bundle"
    )
    generate_parser.add_argument(
        "--sign", 
        action="store_true",
        help="Include digital signature"
    )

    # Diff command
    diff_parser = subparsers.add_parser("diff", help="Compare two scan results")
    diff_parser.add_argument("baseline", help="Baseline scan result JSON file")
    diff_parser.add_argument("current", help="Current scan result JSON file")
    diff_parser.add_argument(
        "--output-dir", 
        "-o", 
        type=str, 
        default="reports",
        help="Output directory"
    )
    diff_parser.add_argument(
        "--format", 
        "-f", 
        type=str, 
        default="html",
        help="Output format"
    )

    # Themes command
    subparsers.add_parser("themes", help="List available themes")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate scan result file")
    validate_parser.add_argument("scan_file", help="Scan result JSON file to validate")

    # Sample command
    sample_parser = subparsers.add_parser("sample", help="Create sample scan result file")
    sample_parser.add_argument(
        "--output", 
        "-o", 
        type=str,
        help="Output file path (default: sample_scan.json)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Execute command
    if args.command == "generate":
        asyncio.run(generate_reports_command(args))
    elif args.command == "diff":
        asyncio.run(diff_command(args))
    elif args.command == "themes":
        list_themes_command(args)
    elif args.command == "validate":
        validate_scan_command(args)
    elif args.command == "sample":
        create_sample_command(args)


if __name__ == "__main__":
    main()

