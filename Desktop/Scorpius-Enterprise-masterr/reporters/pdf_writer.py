"""
PDF Report Writer
=================

Generate PDF reports with digital signatures, watermarks, and professional styling.
"""

import asyncio
import base64
import io
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

# Isolate WeasyPrint import to prevent Windows loading issues
WEASYPRINT_AVAILABLE = False
weasyprint = None
try:
    # Only try to import if not on Windows or if specifically requested
    import platform
    if platform.system() != 'Windows':
        import weasyprint
        WEASYPRINT_AVAILABLE = True
except ImportError:
    pass

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.platypus.flowables import Image
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    colors = None

from jinja2 import Environment, FileSystemLoader

from .base import ReportContext, TemplatedReporter
from signer.pdf_signer import PDFSigner


class PDFReporter(TemplatedReporter):
    """PDF report generator with advanced features"""
    
    def __init__(
        self, 
        output_dir: Optional[Path] = None, 
        template_dir: Optional[Path] = None,
        use_weasyprint: bool = False  # Default to False for Windows compatibility
    ):
        super().__init__(output_dir, template_dir)
        self.supported_formats = ["pdf"]
        self.use_weasyprint = use_weasyprint
        self.pdf_signer: Optional[PDFSigner] = None
        
        # Setup Jinja2 for HTML templates (if using WeasyPrint)
        if self.use_weasyprint:
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(self.template_dir)),
                autoescape=True
            )
            self._register_html_filters()
            
    def set_pdf_signer(self, signer: PDFSigner) -> None:
        """Set PDF digital signer"""
        self.pdf_signer = signer
        
    def _register_html_filters(self) -> None:
        """Register Jinja2 filters for HTML-to-PDF conversion"""
        
        @self.jinja_env.filter
        def severity_style(severity: str) -> str:
            """Get CSS classes for severity levels"""
            styles = {
                "critical": "background-color: #dc2626; color: white;",
                "high": "background-color: #ea580c; color: white;",
                "medium": "background-color: #d97706; color: white;",
                "low": "background-color: #65a30d; color: white;",
                "info": "background-color: #0891b2; color: white;"
            }
            return styles.get(severity.lower(), "background-color: #6b7280; color: white;")
            
        @self.jinja_env.filter
        def risk_bar_width(score: float, max_score: float = 10.0) -> float:
            """Calculate width percentage for risk score bars"""
            return (score / max_score) * 100
            
    async def generate(
        self,
        context: ReportContext,
        output_path: Optional[Path] = None,
        template_name: str = "pdf_report.html",
        page_size: str = "A4",
        include_charts: bool = True,
        watermark: Optional[Dict[str, Any]] = None,
        sign_pdf: bool = False,
        **kwargs
    ) -> Path:
        """
        Generate PDF report.
        
        Args:
            context: Report context with scan data
            output_path: Optional custom output path
            template_name: Template to use
            page_size: Page size (A4, Letter, etc.)
            include_charts: Whether to include charts
            watermark: Watermark configuration
            sign_pdf: Whether to digitally sign the PDF
            **kwargs: Additional options
        """
        # Check dependencies
        if self.use_weasyprint and not WEASYPRINT_AVAILABLE:
            raise ImportError("WeasyPrint is not available. Install with: pip install weasyprint")
        if not self.use_weasyprint and not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is not available. Install with: pip install reportlab")
            
        # Validate context
        errors = await self.validate_context(context)
        if errors:
            raise ValueError(f"Context validation failed: {'; '.join(errors)}")
            
        # Prepare output path
        if not output_path:
            filename = self.get_default_filename(context)
            output_path = self.output_dir / filename
            
        if self.use_weasyprint:
            return await self._generate_with_weasyprint(
                context, output_path, template_name, include_charts, watermark, sign_pdf, **kwargs
            )
        else:
            return await self._generate_with_reportlab(
                context, output_path, include_charts, watermark, sign_pdf, **kwargs
            )
            
    async def _generate_with_weasyprint(
        self,
        context: ReportContext,
        output_path: Path,
        template_name: str,
        include_charts: bool,
        watermark: Optional[Dict[str, Any]],
        sign_pdf: bool,
        **kwargs
    ) -> Path:
        """Generate PDF using WeasyPrint (HTML to PDF)"""
        
        # Prepare template context
        template_context = self.prepare_template_context(context)
        template_context.update({
            "include_charts": include_charts,
            "for_pdf": True,
            "charts_as_images": True,
            **kwargs
        })
        
        # Generate charts as base64 images for PDF
        if include_charts:
            template_context["chart_images"] = await self._generate_chart_images(
                template_context["charts"]
            )
            
        # Render HTML template
        html_content = self.render_template(template_name, template_context)
        
        # Add watermark to HTML if specified
        if watermark:
            html_content = self._add_html_watermark(html_content, watermark)
            
        # Convert HTML to PDF
        pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
        
        # Write to temporary file first
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(pdf_bytes)
            temp_path = Path(temp_file.name)
            
        # Sign PDF if requested
        if sign_pdf and self.pdf_signer:
            signed_path = await self.pdf_signer.sign_pdf(temp_path, output_path)
            temp_path.unlink()  # Clean up temporary file
            return signed_path
        else:
            # Move temp file to final location
            output_path.parent.mkdir(parents=True, exist_ok=True)
            temp_path.rename(output_path)
            return output_path
            
    async def _generate_with_reportlab(
        self,
        context: ReportContext,
        output_path: Path,
        include_charts: bool,
        watermark: Optional[Dict[str, Any]],
        sign_pdf: bool,
        **kwargs
    ) -> Path:
        """Generate PDF using ReportLab (programmatic approach)"""
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build content
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        # Title page
        story.append(Paragraph(context.metadata.title, title_style))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Generated: {context.metadata.created_at.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(context.metadata.description, styles['Normal']))
        story.append(PageBreak())
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        stats = context.get_aggregated_stats()
        
        summary_data = [
            ['Severity', 'Count'],
            ['Critical', str(stats.get('critical_issues', 0))],
            ['High', str(stats.get('high_issues', 0))],
            ['Medium', str(stats.get('medium_issues', 0))],
            ['Low', str(stats.get('low_issues', 0))],
            ['Info', str(stats.get('info_issues', 0))],
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 1*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 24))
        
        # Charts
        if include_charts:
            charts = self.prepare_charts_data(context)
            
            # Severity distribution pie chart
            story.append(Paragraph("Vulnerability Distribution", heading_style))
            pie_chart = self._create_pie_chart(charts["severity_distribution"])
            story.append(pie_chart)
            story.append(Spacer(1, 24))
            
        # Detailed findings
        story.append(Paragraph("Detailed Findings", heading_style))
        
        for scan in context.scan_results:
            story.append(Paragraph(f"Project: {scan.project_name}", styles['Heading3']))
            
            for vuln in scan.vulnerabilities:
                # Vulnerability header
                vuln_title = f"{vuln.title} ({vuln.severity.upper()})"
                story.append(Paragraph(vuln_title, styles['Heading4']))
                
                # Description
                story.append(Paragraph(vuln.description, styles['Normal']))
                story.append(Spacer(1, 6))
                
                # Details table
                details_data = [
                    ['Property', 'Value'],
                    ['Risk Score', f"{vuln.risk_score:.1f}/10"],
                    ['Confidence', f"{vuln.confidence * 100:.1f}%"],
                    ['Category', vuln.category.value],
                ]
                
                if vuln.function_name:
                    details_data.append(['Function', vuln.function_name])
                if vuln.line_number:
                    details_data.append(['Line', str(vuln.line_number)])
                    
                details_table = Table(details_data, colWidths=[2*inch, 3*inch])
                details_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                
                story.append(details_table)
                
                # Recommendation
                if vuln.recommendation:
                    story.append(Spacer(1, 6))
                    story.append(Paragraph("Recommendation:", styles['Heading5']))
                    story.append(Paragraph(vuln.recommendation, styles['Normal']))
                    
                story.append(Spacer(1, 12))
                
        # Add watermark if specified
        if watermark:
            # ReportLab watermark implementation would go here
            pass
            
        # Build PDF
        doc.build(story)
        
        # Sign PDF if requested
        if sign_pdf and self.pdf_signer:
            return await self.pdf_signer.sign_pdf(output_path, output_path)
            
        return output_path
        
    def _create_pie_chart(self, severity_data: Dict[str, Any]) -> Drawing:
        """Create a pie chart using ReportLab"""
        drawing = Drawing(400, 200)
        pie = Pie()
        pie.x = 50
        pie.y = 50
        pie.width = 100
        pie.height = 100
        pie.data = severity_data["values"]
        pie.labels = severity_data["labels"]
        pie.slices.strokeColor = colors.white
        pie.slices.strokeWidth = 1
        
        # Set colors
        colors_map = {
            "Critical": colors.red,
            "High": colors.orange,
            "Medium": colors.yellow,
            "Low": colors.green,
            "Info": colors.blue
        }
        
        for i, label in enumerate(severity_data["labels"]):
            pie.slices[i].fillColor = colors_map.get(label, colors.gray)
            
        drawing.add(pie)
        return drawing
        
    async def _generate_chart_images(self, charts_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate chart images as base64 strings for HTML templates"""
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        
        chart_images = {}
        
        # Severity distribution pie chart
        if charts_data.get("severity_distribution"):
            fig, ax = plt.subplots(figsize=(8, 6))
            data = charts_data["severity_distribution"]
            
            wedges, texts, autotexts = ax.pie(
                data["values"],
                labels=data["labels"],
                colors=data["colors"],
                autopct='%1.1f%%',
                startangle=90
            )
            
            ax.set_title('Vulnerability Distribution by Severity')
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            chart_images["severity_pie"] = f"data:image/png;base64,{image_base64}"
            
            plt.close(fig)
            buffer.close()
            
        return chart_images
        
    def _add_html_watermark(self, html_content: str, watermark: Dict[str, Any]) -> str:
        """Add watermark to HTML content"""
        watermark_css = f"""
        <style>
        .watermark {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 72px;
            color: rgba(0, 0, 0, {watermark.get('opacity', 0.1)});
            z-index: -1;
            pointer-events: none;
            font-weight: bold;
            user-select: none;
        }}
        </style>
        """
        
        watermark_div = f'<div class="watermark">{watermark.get("text", "CONFIDENTIAL")}</div>'
        
        # Insert watermark CSS and div
        if '<head>' in html_content:
            html_content = html_content.replace('<head>', f'<head>{watermark_css}')
        if '<body>' in html_content:
            html_content = html_content.replace('<body>', f'<body>{watermark_div}')
            
        return html_content
        
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render Jinja2 template"""
        if self.use_weasyprint:
            template = self.jinja_env.get_template(template_name)
            return template.render(**context)
        else:
            # For ReportLab, we don't use templates
            return ""
            
    def get_file_extension(self) -> str:
        """Get file extension for PDF reports"""
        return "pdf"


# Create default PDF template if it doesn't exist
def create_default_pdf_template(template_dir: Path) -> None:
    """Create default PDF HTML template"""
    template_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_template = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ metadata.title }}</title>
    <style>
        @page {
            size: A4;
            margin: 1in;
            @bottom-center {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 10px;
                color: #666;
            }
        }
        
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }
        
        .header {
            text-align: center;
            border-bottom: 2px solid #333;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        
        .title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .subtitle {
            font-size: 14px;
            color: #666;
        }
        
        .summary-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        .summary-table th,
        .summary-table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }
        
        .summary-table th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        
        .severity-critical { background-color: #dc2626; color: white; }
        .severity-high { background-color: #ea580c; color: white; }
        .severity-medium { background-color: #d97706; color: white; }
        .severity-low { background-color: #65a30d; color: white; }
        .severity-info { background-color: #0891b2; color: white; }
        
        .vulnerability {
            border: 1px solid #ddd;
            margin: 15px 0;
            padding: 15px;
            page-break-inside: avoid;
        }
        
        .vulnerability h3 {
            margin-top: 0;
            color: #333;
        }
        
        .vulnerability-meta {
            background-color: #f9f9f9;
            padding: 10px;
            margin: 10px 0;
            border-left: 4px solid #0891b2;
        }
        
        .page-break {
            page-break-before: always;
        }
        
        .chart-placeholder {
            text-align: center;
            padding: 40px;
            background-color: #f5f5f5;
            border: 1px dashed #ccc;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <div class="title">{{ metadata.title }}</div>
        <div class="subtitle">{{ metadata.description }}</div>
        <div class="subtitle">Generated: {{ generated_at }}</div>
    </div>

    <!-- Executive Summary -->
    <h1>Executive Summary</h1>
    <table class="summary-table">
        <thead>
            <tr>
                <th>Severity</th>
                <th>Count</th>
                <th>Percentage</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td class="severity-critical">Critical</td>
                <td>{{ stats.critical_issues }}</td>
                <td>{{ ((stats.critical_issues / stats.total_issues) * 100) | round(1) if stats.total_issues > 0 else 0 }}%</td>
            </tr>
            <tr>
                <td class="severity-high">High</td>
                <td>{{ stats.high_issues }}</td>
                <td>{{ ((stats.high_issues / stats.total_issues) * 100) | round(1) if stats.total_issues > 0 else 0 }}%</td>
            </tr>
            <tr>
                <td class="severity-medium">Medium</td>
                <td>{{ stats.medium_issues }}</td>
                <td>{{ ((stats.medium_issues / stats.total_issues) * 100) | round(1) if stats.total_issues > 0 else 0 }}%</td>
            </tr>
            <tr>
                <td class="severity-low">Low</td>
                <td>{{ stats.low_issues }}</td>
                <td>{{ ((stats.low_issues / stats.total_issues) * 100) | round(1) if stats.total_issues > 0 else 0 }}%</td>
            </tr>
            <tr>
                <td class="severity-info">Info</td>
                <td>{{ stats.info_issues }}</td>
                <td>{{ ((stats.info_issues / stats.total_issues) * 100) | round(1) if stats.total_issues > 0 else 0 }}%</td>
            </tr>
        </tbody>
    </table>

    {% if include_charts and chart_images %}
    <h2>Vulnerability Analysis</h2>
    {% if chart_images.severity_pie %}
    <img src="{{ chart_images.severity_pie }}" alt="Severity Distribution" style="max-width: 100%; height: auto;">
    {% endif %}
    {% endif %}

    <div class="page-break"></div>

    <!-- Detailed Findings -->
    <h1>Detailed Findings</h1>
    
    {% for scan in scan_results %}
    <h2>{{ scan.project_name }}</h2>
    
    {% for vuln in scan.vulnerabilities %}
    <div class="vulnerability">
        <h3>{{ vuln.title }} 
            <span class="severity-{{ vuln.severity }}" style="padding: 4px 8px; border-radius: 4px; font-size: 12px; margin-left: 10px;">
                {{ vuln.severity.upper() }}
            </span>
        </h3>
        
        <p><strong>Description:</strong> {{ vuln.description }}</p>
        
        <div class="vulnerability-meta">
            <p><strong>Risk Score:</strong> {{ vuln.risk_score }}/10</p>
            <p><strong>Confidence:</strong> {{ (vuln.confidence * 100) | round(1) }}%</p>
            <p><strong>Category:</strong> {{ vuln.category }}</p>
            {% if vuln.function_name %}<p><strong>Function:</strong> {{ vuln.function_name }}</p>{% endif %}
            {% if vuln.line_number %}<p><strong>Line:</strong> {{ vuln.line_number }}</p>{% endif %}
        </div>
        
        {% if vuln.code_snippet %}
        <p><strong>Code Location:</strong></p>
        <pre style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto;">{{ vuln.code_snippet }}</pre>
        {% endif %}
        
        {% if vuln.recommendation %}
        <p><strong>Recommendation:</strong></p>
        <div style="background-color: #e3f2fd; padding: 10px; border-left: 4px solid #2196f3;">
            {{ vuln.recommendation }}
        </div>
        {% endif %}
    </div>
    {% endfor %}
    {% endfor %}

    <!-- Scan Information -->
    <div class="page-break"></div>
    <h1>Scan Information</h1>
    {% for scan in scan_results %}
    <h3>{{ scan.project_name }}</h3>
    <ul>
        <li><strong>Scan ID:</strong> {{ scan.id }}</li>
        <li><strong>Created:</strong> {{ scan.created_at }}</li>
        <li><strong>Status:</strong> {{ scan.status }}</li>
        <li><strong>Total Contracts:</strong> {{ scan.contracts | length }}</li>
        <li><strong>Total Issues:</strong> {{ scan.total_issues }}</li>
    </ul>
    {% endfor %}
</body>
</html>'''
    
    template_path = template_dir / "pdf_report.html"
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(pdf_template)

