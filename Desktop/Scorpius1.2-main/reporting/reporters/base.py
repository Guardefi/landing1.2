"""
Base Reporter Classes
====================

Abstract base classes and interfaces for all report format writers.
"""

import asyncio
import hashlib
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from models import ScanResult


class ReportMetadata:
    """Report metadata container"""
    
    def __init__(
        self,
        title: str,
        description: str = "",
        author: str = "",
        created_at: Optional[datetime] = None,
        version: str = "1.0",
        template: str = "default",
        watermark: Optional[Dict[str, Any]] = None,
        custom_fields: Optional[Dict[str, Any]] = None
    ):
        self.title = title
        self.description = description
        self.author = author
        self.created_at = created_at or datetime.utcnow()
        self.version = version
        self.template = template
        self.watermark = watermark or {}
        self.custom_fields = custom_fields or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        return {
            "title": self.title,
            "description": self.description,
            "author": self.author,
            "created_at": self.created_at.isoformat(),
            "version": self.version,
            "template": self.template,
            "watermark": self.watermark,
            "custom_fields": self.custom_fields,
        }


class ReportSection:
    """Report section container"""
    
    def __init__(
        self,
        name: str,
        title: str,
        content: str = "",
        order: int = 0,
        include_in_toc: bool = True,
        level: int = 1,
        data: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.title = title
        self.content = content
        self.order = order
        self.include_in_toc = include_in_toc
        self.level = level
        self.data = data or {}
        self.subsections: List[ReportSection] = []
        
    def add_subsection(self, subsection: 'ReportSection') -> None:
        """Add a subsection"""
        subsection.level = self.level + 1
        self.subsections.append(subsection)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert section to dictionary"""
        return {
            "name": self.name,
            "title": self.title,
            "content": self.content,
            "order": self.order,
            "include_in_toc": self.include_in_toc,
            "level": self.level,
            "data": self.data,
            "subsections": [sub.to_dict() for sub in self.subsections],
        }


class ReportContext:
    """Complete report context with all data and configuration"""
    
    def __init__(
        self,
        scan_results: List[ScanResult],
        metadata: ReportMetadata,
        config: Optional[Dict[str, Any]] = None,
        template_vars: Optional[Dict[str, Any]] = None
    ):
        self.scan_results = scan_results
        self.metadata = metadata
        self.config = config or {}
        self.template_vars = template_vars or {}
        self.sections: List[ReportSection] = []
        self.charts_data: Dict[str, Any] = {}
        
    def add_section(self, section: ReportSection) -> None:
        """Add a section to the report"""
        self.sections.append(section)
        
    def get_aggregated_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics across all scan results"""
        if not self.scan_results:
            return {}
            
        total_issues = sum(scan.total_issues for scan in self.scan_results)
        critical_issues = sum(scan.critical_issues for scan in self.scan_results)
        high_issues = sum(scan.high_issues for scan in self.scan_results)
        medium_issues = sum(scan.medium_issues for scan in self.scan_results)
        low_issues = sum(scan.low_issues for scan in self.scan_results)
        info_issues = sum(scan.info_issues for scan in self.scan_results)
        
        return {
            "total_scans": len(self.scan_results),
            "total_contracts": sum(len(scan.contracts) for scan in self.scan_results),
            "total_issues": total_issues,
            "critical_issues": critical_issues,
            "high_issues": high_issues,
            "medium_issues": medium_issues,
            "low_issues": low_issues,
            "info_issues": info_issues,
            "scan_dates": [scan.created_at for scan in self.scan_results],
            "projects": list(set(scan.project_name for scan in self.scan_results)),
        }


class BaseReporter(ABC):
    """Abstract base class for all report writers"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = Path(output_dir or "reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.supported_formats: List[str] = []
        
    @abstractmethod
    async def generate(
        self,
        context: ReportContext,
        output_path: Optional[Path] = None,
        **kwargs
    ) -> Path:
        """
        Generate report in the specific format.
        
        Args:
            context: Report context containing all data
            output_path: Optional custom output path
            **kwargs: Additional format-specific options
            
        Returns:
            Path to the generated report file
        """
        pass
        
    @abstractmethod
    def get_file_extension(self) -> str:
        """Get the file extension for this report format"""
        pass
        
    def get_default_filename(self, context: ReportContext) -> str:
        """Generate default filename based on context"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in context.metadata.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')
        return f"{safe_title}_{timestamp}.{self.get_file_extension()}"
        
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of the generated file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
        
    async def validate_context(self, context: ReportContext) -> List[str]:
        """
        Validate report context and return list of validation errors.
        
        Args:
            context: Report context to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        if not context.scan_results:
            errors.append("No scan results provided")
            
        if not context.metadata.title:
            errors.append("Report title is required")
            
        # Validate scan results
        for i, scan in enumerate(context.scan_results):
            if not scan.project_name:
                errors.append(f"Scan {i}: Project name is required")
                
        return errors
        
    def prepare_charts_data(self, context: ReportContext) -> Dict[str, Any]:
        """Prepare data for charts and visualizations"""
        stats = context.get_aggregated_stats()
        
        # Severity distribution for pie chart
        severity_data = {
            "labels": ["Critical", "High", "Medium", "Low", "Info"],
            "values": [
                stats.get("critical_issues", 0),
                stats.get("high_issues", 0),
                stats.get("medium_issues", 0),
                stats.get("low_issues", 0),
                stats.get("info_issues", 0),
            ],
            "colors": ["#dc2626", "#ea580c", "#d97706", "#65a30d", "#0891b2"]
        }
        
        # Timeline data for trends
        timeline_data = []
        for scan in context.scan_results:
            timeline_data.append({
                "date": scan.created_at.strftime("%Y-%m-%d"),
                "project": scan.project_name,
                "total_issues": scan.total_issues,
                "critical": scan.critical_issues,
                "high": scan.high_issues,
                "medium": scan.medium_issues,
                "low": scan.low_issues,
            })
            
        # Risk score distribution
        risk_scores = []
        for scan in context.scan_results:
            risk_summary = scan.get_risk_summary()
            risk_scores.append({
                "project": scan.project_name,
                "risk_score": risk_summary["risk_score"],
                "overall_risk": risk_summary["overall_risk"],
            })
            
        return {
            "severity_distribution": severity_data,
            "timeline": timeline_data,
            "risk_scores": risk_scores,
            "summary_stats": stats,
        }


class TemplatedReporter(BaseReporter):
    """Base class for template-based reporters (HTML, Markdown, etc.)"""
    
    def __init__(self, output_dir: Optional[Path] = None, template_dir: Optional[Path] = None):
        super().__init__(output_dir)
        self.template_dir = Path(template_dir or "templates")
        
    @abstractmethod
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render template with context data"""
        pass
        
    def prepare_template_context(self, context: ReportContext) -> Dict[str, Any]:
        """Prepare template context with all necessary data"""
        return {
            "metadata": context.metadata.to_dict(),
            "scan_results": [self._serialize_scan_result(scan) for scan in context.scan_results],
            "sections": [section.to_dict() for section in context.sections],
            "stats": context.get_aggregated_stats(),
            "charts": self.prepare_charts_data(context),
            "config": context.config,
            "template_vars": context.template_vars,
            "generated_at": datetime.now().isoformat(),
        }
        
    def _serialize_scan_result(self, scan: ScanResult) -> Dict[str, Any]:
        """Serialize scan result to dictionary for templates"""
        return scan.dict()


class StreamingReporter(BaseReporter):
    """Base class for streaming/progressive report generation"""
    
    async def generate_stream(
        self,
        context: ReportContext,
        progress_callback: Optional[callable] = None,
        **kwargs
    ):
        """
        Generate report with streaming/progressive updates.
        
        Args:
            context: Report context
            progress_callback: Optional callback for progress updates
            **kwargs: Additional options
        """
        if progress_callback:
            await progress_callback(0.0, "Starting report generation...")
            
        # Override in subclasses for streaming implementation
        result = await self.generate(context, **kwargs)
        
        if progress_callback:
            await progress_callback(1.0, "Report generation completed")
            
        return result


class MultiFormatReporter:
    """Manager for generating reports in multiple formats"""
    
    def __init__(self):
        self.reporters: Dict[str, BaseReporter] = {}
        
    def register_reporter(self, format_name: str, reporter: BaseReporter) -> None:
        """Register a reporter for a specific format"""
        self.reporters[format_name] = reporter
        
    async def generate_all(
        self,
        context: ReportContext,
        formats: List[str],
        output_dir: Optional[Path] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Path]:
        """
        Generate reports in multiple formats concurrently.
        
        Args:
            context: Report context
            formats: List of format names to generate
            output_dir: Output directory for all reports
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary mapping format names to output file paths
        """
        results = {}
        total_formats = len(formats)
        
        async def generate_format(format_name: str, index: int) -> tuple[str, Path]:
            if format_name not in self.reporters:
                raise ValueError(f"Unsupported format: {format_name}")
                
            reporter = self.reporters[format_name]
            if output_dir:
                reporter.output_dir = output_dir
                
            if progress_callback:
                await progress_callback(
                    index / total_formats,
                    f"Generating {format_name} report..."
                )
                
            output_path = await reporter.generate(context)
            
            if progress_callback:
                await progress_callback(
                    (index + 1) / total_formats,
                    f"Completed {format_name} report"
                )
                
            return format_name, output_path
            
        # Generate all formats concurrently
        tasks = [
            generate_format(fmt, i) 
            for i, fmt in enumerate(formats)
        ]
        
        completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
        
        for task_result in completed_tasks:
            if isinstance(task_result, Exception):
                raise task_result
            format_name, output_path = task_result
            results[format_name] = output_path
            
        return results
        
    def get_supported_formats(self) -> List[str]:
        """Get list of supported format names"""
        return list(self.reporters.keys())


# Export all classes
__all__ = [
    "ReportMetadata",
    "ReportSection", 
    "ReportContext",
    "BaseReporter",
    "TemplatedReporter",
    "StreamingReporter",
    "MultiFormatReporter",
]

