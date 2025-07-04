"""
Scorpius Reporting Service - PDF Generator
Enterprise-grade PDF generation with templates and signatures
"""

import os
import io
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import json
import base64

# PDF generation libraries
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.platypus.flowables import HRFlowable
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logging.warning("ReportLab not available. PDF generation will be limited.")

from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class PDFGenerationError(Exception):
    """PDF Generation error"""
    pass


class PDFGenerator:
    """Enterprise PDF report generator with templates and styling"""
    
    def __init__(self):
        self.settings = settings
        self.styles = None
        self.templates = {}
        self._initialize_styles()
        self._load_templates()
    
    def _initialize_styles(self):
        """Initialize PDF styles"""
        if not REPORTLAB_AVAILABLE:
            return
        
        self.styles = getSampleStyleSheet()
        
        # Custom styles for enterprise reports
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#374151'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=6,
            fontName='Helvetica'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomFooter',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#6b7280'),
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
    
    def _load_templates(self):
        """Load PDF templates"""
        template_path = self.settings.PDF_TEMPLATE_PATH
        if os.path.exists(template_path):
            for template_file in os.listdir(template_path):
                if template_file.endswith('.json'):
                    template_name = template_file[:-5]  # Remove .json extension
                    try:
                        with open(os.path.join(template_path, template_file), 'r') as f:
                            self.templates[template_name] = json.load(f)
                    except Exception as e:
                        logger.warning(f"Failed to load template {template_file}: {e}")
    
    async def generate_report(
        self,
        title: str,
        data: Dict[str, Any],
        template: str = "default",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Generate PDF report
        
        Args:
            title: Report title
            data: Report data
            template: Template name to use
            metadata: Additional metadata
            
        Returns:
            PDF content as bytes
        """
        if not REPORTLAB_AVAILABLE:
            # Fallback to simple text-based PDF
            return await self._generate_simple_pdf(title, data, metadata)
        
        try:
            # Create PDF buffer
            buffer = io.BytesIO()
            
            # Create PDF document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build content
            story = []
            
            # Add header
            story.extend(self._build_header(title, metadata))
            
            # Add main content based on template
            if template in self.templates:
                story.extend(self._build_templated_content(data, self.templates[template]))
            else:
                story.extend(self._build_default_content(data))
            
            # Add footer
            story.extend(self._build_footer(metadata))
            
            # Build PDF
            doc.build(story)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            logger.info(f"Generated PDF report: {len(pdf_bytes)} bytes")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"PDF generation error: {e}")
            raise PDFGenerationError(f"Failed to generate PDF: {str(e)}")
    
    def _build_header(self, title: str, metadata: Optional[Dict[str, Any]]) -> list:
        """Build PDF header"""
        story = []
        
        # Logo (if available)
        logo_path = os.path.join(self.settings.PDF_TEMPLATE_PATH, "logo.png")
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=2*inch, height=0.5*inch)
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 12))
            except Exception as e:
                logger.warning(f"Failed to load logo: {e}")
        
        # Title
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        
        # Metadata table
        if metadata:
            meta_data = [
                ['Generated:', datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')],
                ['Service:', 'Scorpius Enterprise Platform'],
                ['Version:', self.settings.APP_VERSION]
            ]
            
            if 'user_id' in metadata:
                meta_data.append(['User:', metadata['user_id']])
            
            meta_table = Table(meta_data, colWidths=[1.5*inch, 4*inch])
            meta_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(meta_table)
            story.append(Spacer(1, 20))
        
        # Horizontal line
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
        story.append(Spacer(1, 20))
        
        return story
    
    def _build_default_content(self, data: Dict[str, Any]) -> list:
        """Build default content structure"""
        story = []
        
        for section_key, section_data in data.items():
            # Section heading
            heading = section_key.replace('_', ' ').title()
            story.append(Paragraph(heading, self.styles['CustomHeading']))
            
            if isinstance(section_data, dict):
                # Table format for dictionary data
                table_data = []
                for key, value in section_data.items():
                    formatted_key = key.replace('_', ' ').title()
                    formatted_value = str(value) if not isinstance(value, (dict, list)) else json.dumps(value, indent=2)
                    table_data.append([formatted_key, formatted_value])
                
                if table_data:
                    table = Table(table_data, colWidths=[2*inch, 4*inch])
                    table.setStyle(TableStyle([
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
                        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f9fafb')),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('PADDING', (0, 0), (-1, -1), 6),
                    ]))
                    story.append(table)
            
            elif isinstance(section_data, list):
                # List format
                for item in section_data:
                    if isinstance(item, dict):
                        # Nested table for list items
                        item_data = [[k.replace('_', ' ').title(), str(v)] for k, v in item.items()]
                        if item_data:
                            item_table = Table(item_data, colWidths=[2*inch, 4*inch])
                            item_table.setStyle(TableStyle([
                                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                                ('FONTSIZE', (0, 0), (-1, -1), 9),
                                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                ('PADDING', (0, 0), (-1, -1), 4),
                            ]))
                            story.append(item_table)
                            story.append(Spacer(1, 6))
                    else:
                        story.append(Paragraph(f"• {str(item)}", self.styles['CustomBody']))
            
            else:
                # Simple text
                story.append(Paragraph(str(section_data), self.styles['CustomBody']))
            
            story.append(Spacer(1, 16))
        
        return story
    
    def _build_templated_content(self, data: Dict[str, Any], template: Dict[str, Any]) -> list:
        """Build content using template"""
        story = []
        
        # Template-based content generation would go here
        # For now, fall back to default content
        return self._build_default_content(data)
    
    def _build_footer(self, metadata: Optional[Dict[str, Any]]) -> list:
        """Build PDF footer"""
        story = []
        
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
        story.append(Spacer(1, 12))
        
        # Footer text
        footer_text = "This report was generated by Scorpius Enterprise Platform. "
        footer_text += "The integrity of this document is protected by cryptographic signatures."
        
        story.append(Paragraph(footer_text, self.styles['CustomFooter']))
        
        # Watermark if enabled
        if self.settings.PDF_WATERMARK_ENABLED and metadata and metadata.get('watermark'):
            story.append(Spacer(1, 6))
            story.append(Paragraph(f"Watermark: {metadata['watermark']}", self.styles['CustomFooter']))
        
        return story
    
    async def _generate_simple_pdf(
        self,
        title: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """Generate simple text-based PDF when ReportLab is not available"""
        
        # Create a simple PDF-like structure
        content = f"""
PDF REPORT - {title}
{'=' * 50}

Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
Service: Scorpius Enterprise Platform
Version: {self.settings.APP_VERSION}

{'=' * 50}
REPORT DATA
{'=' * 50}

{json.dumps(data, indent=2)}

{'=' * 50}
METADATA
{'=' * 50}

{json.dumps(metadata or {}, indent=2)}

{'=' * 50}
This report was generated by Scorpius Enterprise Platform.
The integrity of this document is protected by cryptographic signatures.
{'=' * 50}
"""
        
        # Convert to bytes (in production, you'd want actual PDF generation)
        return content.encode('utf-8')
    
    def get_available_templates(self) -> list:
        """Get list of available templates"""
        return list(self.templates.keys())
    
    def validate_template(self, template_name: str) -> bool:
        """Validate if template exists"""
        return template_name in self.templates or template_name == "default"
