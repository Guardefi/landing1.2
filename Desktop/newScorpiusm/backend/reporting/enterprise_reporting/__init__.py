"""
Scorpius Enterprise Reporting Module
====================================

A comprehensive, plug-and-play reporting system that transforms raw scan and mempool data
into auditor-grade deliverables with full white-label capabilities.

Features:
- Multi-format output (PDF, HTML, Markdown, SARIF-v2, CSV)
- Jinja2 templating with theme packs
- Live data binding with WebSocket updates
- Role-based publishing workflow
- Client-facing portals with signed URLs
- Smart diffing and change tracking
- Embeddable widgets
- Digital signatures and watermarks
"""

from .api import create_reporting_router
from .core import ReportBuilder, ReportEngine, ReportExporter
from .diff import ReportDiffEngine
from .models import ReportAuditLog, ReportJob, ReportTemplate
from .themes import ThemeManager
from .widgets import WidgetRegistry

__version__ = "1.0.0"
__author__ = "Scorpius Security"

__all__ = [
    "ReportEngine",
    "ReportBuilder",
    "ReportExporter",
    "ReportTemplate",
    "ReportJob",
    "ReportAuditLog",
    "create_reporting_router",
    "ThemeManager",
    "WidgetRegistry",
    "ReportDiffEngine",
]
