"""
Core Report Generation Engine
============================

The main report generation engine that orchestrates the entire reporting process.
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import asyncio
from dataclasses import dataclass

from jinja2 import Environment, FileSystemLoader, select_autoescape

# Handle both relative and absolute imports  
try:
    from .models import ReportAuditLog, ReportJob, ReportTemplate
    from .themes import ThemeManager
    from .widgets import WidgetRegistry
except ImportError:
    from models import ReportAuditLog, ReportJob, ReportTemplate
    from themes import ThemeManager
    from widgets import WidgetRegistry

# Report formats
WEASYPRINT_AVAILABLE = False  # Disabled for Windows compatibility

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ReportContext:
    """Report generation context data"""
    scan_result: Dict[str, Any]
    template_name: str
    theme_name: str = "default"
    output_formats: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.output_formats is None:
            self.output_formats = ["html"]
        if self.metadata is None:
            self.metadata = {}


class ReportEngine:
    """Main report generation engine"""

    def __init__(self, db_session=None, templates_dir: str = "templates", output_dir: str = "reports"):
        self.db_session = db_session
        self.templates_dir = Path(templates_dir)
        self.output_dir = Path(output_dir)
        self.theme_manager = ThemeManager()
        self.widget_registry = WidgetRegistry()
        self._setup_jinja()
        self._ensure_directories()

    def _setup_jinja(self):
        """Setup Jinja2 template environment"""
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def _ensure_directories(self):
        """Ensure output directories exist"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

    async def generate_report(self, context: ReportContext) -> Dict[str, Path]:
        """Generate reports in multiple formats"""
        logger.info(f"Generating report for template: {context.template_name}")
        
        generated_files = {}
        
        try:
            # Load template
            template = self.env.get_template(f"{context.template_name}.html")
            
            # Prepare template context
            template_context = self._prepare_template_context(context)
            
            # Generate HTML first (base format)
            html_content = template.render(**template_context)
            
            # Generate each requested format
            for format_name in context.output_formats:
                output_path = self.output_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_name}"
                
                if format_name == "html":
                    await self._save_html(html_content, output_path)
                elif format_name == "pdf":
                    await self._generate_pdf(html_content, output_path, context.metadata)
                elif format_name == "json":
                    await self._generate_json(context, output_path)
                elif format_name == "csv":
                    await self._generate_csv(context, output_path)
                elif format_name == "sarif":
                    await self._generate_sarif(context, output_path)
                
                generated_files[format_name] = output_path
                logger.info(f"Generated {format_name} report: {output_path}")
            
            return generated_files
            
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            raise

    def _prepare_template_context(self, context: ReportContext) -> Dict[str, Any]:
        """Prepare context data for template rendering"""
        return {
            "scan_result": context.scan_result,
            "metadata": context.metadata,
            "theme": self.theme_manager.get_theme(context.theme_name),
            "widgets": self.widget_registry.get_widgets(),
            "generated_at": datetime.utcnow().isoformat(),
            "report_id": context.metadata.get("report_id", "unknown")
        }

    async def _save_html(self, html_content: str, output_path: Path) -> None:
        """Save HTML content to file"""
        output_path.write_text(html_content, encoding="utf-8")

    async def _generate_pdf(self, html_content: str, output_path: Path, config: Dict[str, Any]) -> None:
        """Generate PDF using ReportLab (WeasyPrint disabled for Windows compatibility)"""
        if REPORTLAB_AVAILABLE:
            # Use ReportLab for PDF generation
            doc = SimpleDocTemplate(str(output_path), pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Simple HTML to text conversion for PDF
            import re
            text_content = re.sub('<[^<]+?>', '', html_content)
            story.append(Paragraph(text_content, styles['Normal']))
            
            doc.build(story)
        else:
            # Fallback: create a simple text-based file
            with open(output_path.with_suffix('.txt'), 'w', encoding='utf-8') as f:
                import re
                text_content = re.sub('<[^<]+?>', '', html_content)
                f.write(text_content)

    async def _generate_json(self, context: ReportContext, output_path: Path) -> None:
        """Generate JSON report"""
        report_data = {
            "report_id": context.metadata.get("report_id", "unknown"),
            "generated_at": datetime.utcnow().isoformat(),
            "scan_result": context.scan_result,
            "metadata": context.metadata,
            "format": "json",
            "version": "1.0"
        }
        
        output_path.write_text(
            json.dumps(report_data, indent=2, default=str), 
            encoding="utf-8"
        )

    async def _generate_csv(self, context: ReportContext, output_path: Path) -> None:
        """Generate CSV report"""
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write headers
            writer.writerow(['Finding ID', 'Severity', 'Title', 'Description', 'Line'])
            
            # Write findings from scan result
            findings = context.scan_result.get('findings', [])
            for finding in findings:
                writer.writerow([
                    finding.get('id', ''),
                    finding.get('severity', ''),
                    finding.get('title', ''),
                    finding.get('description', ''),
                    finding.get('line', '')
                ])

    async def _generate_sarif(self, context: ReportContext, output_path: Path) -> None:
        """Generate SARIF v2.1.0 report"""
        sarif_report = {
            "version": "2.1.0",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": "Scorpius Scanner",
                        "version": "1.0.0",
                        "informationUri": "https://example.com/scorpius"
                    }
                },
                "results": []
            }]
        }
        
        # Convert findings to SARIF format
        findings = context.scan_result.get('findings', [])
        for finding in findings:
            sarif_result = {
                "ruleId": finding.get('rule_id', 'unknown'),
                "message": {
                    "text": finding.get('description', '')
                },
                "level": self._map_severity_to_sarif(finding.get('severity', 'info')),
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": finding.get('file', 'unknown')
                        },
                        "region": {
                            "startLine": finding.get('line', 1)
                        }
                    }
                }]
            }
            sarif_report["runs"][0]["results"].append(sarif_result)
        
        output_path.write_text(
            json.dumps(sarif_report, indent=2), 
            encoding="utf-8"
        )

    def _map_severity_to_sarif(self, severity: str) -> str:
        """Map severity levels to SARIF levels"""
        mapping = {
            "critical": "error",
            "high": "error", 
            "medium": "warning",
            "low": "note",
            "info": "note"
        }
        return mapping.get(severity.lower(), "note")


class ReportExporter:
    """Utility class for exporting reports"""
    
    def __init__(self, db_session):
        self.db_session = db_session
    
    async def export_reports(self, report_ids: List[str], format: str) -> bytes:
        """Export multiple reports to specified format"""
        # Placeholder implementation
        return b"exported_data"
    
    async def create_audit_bundle(self, report_ids: List[str]) -> bytes:
        """Create a comprehensive audit bundle"""
        # Placeholder implementation  
        return b"audit_bundle_data"


class ReportProcessor:
    """Process and validate report data"""
    
    def __init__(self, engine: ReportEngine):
        self.engine = engine
        
    async def process_scan_result(self, scan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw scan data into structured format"""
        processed = {
            "scan_id": scan_data.get("scan_id"),
            "contract_address": scan_data.get("contract_address"),
            "findings": [],
            "summary": {
                "total_findings": 0,
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
                "info_count": 0
            }
        }
        
        # Process findings
        for finding in scan_data.get("findings", []):
            processed_finding = {
                "id": finding.get("id"),
                "title": finding.get("title"),
                "description": finding.get("description"),
                "severity": finding.get("severity", "info"),
                "category": finding.get("category"),
                "file": finding.get("file"),
                "line": finding.get("line"),
                "confidence": finding.get("confidence", "medium")
            }
            processed["findings"].append(processed_finding)
            
            # Update summary counts
            severity = processed_finding["severity"].lower()
            if severity in processed["summary"]:
                processed["summary"][f"{severity}_count"] += 1
            processed["summary"]["total_findings"] += 1
        
        return processed
