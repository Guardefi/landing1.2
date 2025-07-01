"""
Markdown Report Writer
======================

Generate Markdown reports for documentation and collaborative review.
"""

from pathlib import Path
from typing import Dict, Any, Optional

from .base import BaseReporter, ReportContext


class MarkdownReporter(BaseReporter):
    """Markdown report generator for documentation and review"""

    def __init__(self, output_dir: Optional[Path] = None):
        super().__init__(output_dir)
        
    async def generate(
        self,
        context: ReportContext,
        output_path: Optional[Path] = None,
        **kwargs
    ) -> Path:
        """Generate Markdown report"""
        # Validate context
        errors = await self.validate_context(context)
        if errors:
            raise ValueError(f"Context validation failed: {'; '.join(errors)}")
            
        # Prepare output path
        if not output_path:
            filename = self.get_default_filename(context)
            output_path = self.output_dir / filename
            
        content = self._generate_markdown_content(context)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return output_path
    
    def get_file_extension(self) -> str:
        """Get the file extension for Markdown reports"""
        return "md"
        
    async def generate_report(self, context: ReportContext) -> Dict[str, Any]:
        """Generate Markdown report"""
        content = self._generate_markdown_content(context)
        
        output_path = self.output_dir / f"{context.metadata.title.lower().replace(' ', '_')}.md"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return {
            "format": "markdown",
            "file_path": str(output_path),
            "size_bytes": len(content.encode('utf-8')),
            "sections": len(content.split('\n# ')),
        }
    
    def _generate_markdown_content(self, context: ReportContext) -> str:
        """Generate markdown content"""
        lines = []
        
        # Title and metadata
        lines.append(f"# {context.metadata.title}\n")
        lines.append(f"**Description:** {context.metadata.description}\n")
        lines.append(f"**Generated:** {context.metadata.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        lines.append(f"**Version:** {context.metadata.version}\n")
        
        # Executive Summary
        if context.scan_result:
            lines.append("## Executive Summary\n")
            lines.append(f"- **Total Vulnerabilities:** {len(context.scan_result.vulnerabilities)}")
            
            severity_counts = {}
            for vuln in context.scan_result.vulnerabilities:
                severity_counts[vuln.severity] = severity_counts.get(vuln.severity, 0) + 1
            
            for severity, count in severity_counts.items():
                lines.append(f"- **{severity.title()}:** {count}")
            
            lines.append("")
            
            # Vulnerabilities
            lines.append("## Vulnerabilities\n")
            for i, vuln in enumerate(context.scan_result.vulnerabilities, 1):
                lines.append(f"### {i}. {vuln.title}")
                lines.append(f"**Severity:** {vuln.severity}")
                lines.append(f"**Description:** {vuln.description}")
                if vuln.recommendation:
                    lines.append(f"**Recommendation:** {vuln.recommendation}")
                lines.append("")
        
        return "\n".join(lines)