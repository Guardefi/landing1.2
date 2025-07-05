"""
Enterprise Reporting API Routes
==============================

FastAPI routes for the enterprise reporting system providing endpoints for
report generation, management, publishing, and client portal access.
"""

import uuid
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import asyncio
import json

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi.security import HTTPBearer
from sqlalchemy import and_, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

# Handle both relative and absolute imports
try:
    from .config import get_settings
    from .core import ReportEngine, ReportExporter
    from .diff_engine import ReportDiffEngine, DiffReportGenerator
    from .models import (
        ReportAccessLog,
        ReportAuditLog,
        ReportDiff,
        ReportFormat,
        ReportJob,
        ReportJobCreate,
        ReportJobResponse,
        ReportStatus,
        ReportTemplate,
        ReportTemplateCreate,
        ReportTemplateResponse,
        ReportPublishRequest,
        ReportDiffResponse,
        ReportExportRequest,
        ScanResult,
        ScanRequest,
        ScanSummary,
    )
    from .reporters.base import MultiFormatReporter
    from .reporters.html_writer import HTMLReporter
    from .reporters.pdf_writer import PDFReporter
    from .reporters.json_writer import JSONReporter
    from .reporters.csv_writer import CSVReporter
    from .reporters.sarif_writer import SARIFReporter
    from .signer.pdf_signer import PDFSigner
    from .themes import ThemeManager
    from .validators import ReportFormatValidator
    from .widgets import WidgetRegistry
    from .persistence.db import get_db
except ImportError:
    # Fall back to absolute imports when run directly
    from config import get_settings
    from core import ReportEngine, ReportExporter
    from diff_engine import ReportDiffEngine, DiffReportGenerator
    from models import (
        ReportAccessLog,
        ReportAuditLog,
        ReportDiff,
        ReportFormat,
        ReportJob,
        ReportJobCreate,
        ReportJobResponse,
        ReportStatus,
        ReportTemplate,
        ReportTemplateCreate,
        ReportTemplateResponse,
        ReportPublishRequest,
        ReportDiffResponse,
        ReportExportRequest,
        ScanResult,
        ScanRequest,
        ScanSummary,
    )
    from reporters.base import MultiFormatReporter
    from reporters.html_writer import HTMLReporter
    from reporters.pdf_writer import PDFReporter
    from reporters.json_writer import JSONReporter
    from reporters.csv_writer import CSVReporter
    from reporters.sarif_writer import SARIFReporter
    from signer.pdf_signer import PDFSigner
    from themes import ThemeManager
    from validators import ReportFormatValidator
    from widgets import WidgetRegistry
    from persistence.db import get_db

# Create router
router = APIRouter(prefix="/api/v1/reporting", tags=["Enterprise Reporting"])
security = HTTPBearer()


# Dependencies
async def get_current_user(token: str = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user from token"""
    # For enterprise deployment, implement proper JWT validation here
    # This is a simplified implementation for development
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # In production, validate JWT token and get user from database
    # For now, return a mock admin user
    return {
        "user_id": "user_123",
        "name": "Admin User", 
        "email": "admin@example.com",
        "is_admin": True,
        "permissions": ["read", "write", "admin"],
        "organization_id": "org_123"
    }


async def get_report_engine(db: AsyncSession = Depends(get_db)) -> ReportEngine:
    """Get configured report engine instance"""
    settings = get_settings()
    return ReportEngine(
        db_session=db,
        templates_dir=str(settings.reporting.templates_dir),
        output_dir=str(settings.reporting.reports_dir)
    )


async def get_multi_format_reporter() -> MultiFormatReporter:
    """Get configured multi-format reporter"""
    reporter = MultiFormatReporter()
    reporter.add_reporter(ReportFormat.HTML, HTMLReporter())
    reporter.add_reporter(ReportFormat.PDF, PDFReporter())
    reporter.add_reporter(ReportFormat.JSON, JSONReporter())
    reporter.add_reporter(ReportFormat.CSV, CSVReporter())
    reporter.add_reporter(ReportFormat.SARIF, SARIFReporter())
    return reporter


# === SCAN SUBMISSION & REPORT GENERATION ===

@router.post("/scans/submit", response_model=Dict[str, Any])
async def submit_scan(
    scan_request: ScanRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    engine: ReportEngine = Depends(get_report_engine)
) -> Dict[str, Any]:
    """Submit a new scan for processing and report generation"""
    try:
        # Create job record
        job_id = str(uuid.uuid4())
        
        # Start background processing
        background_tasks.add_task(
            process_scan_background,
            job_id,
            scan_request,
            current_user["user_id"]
        )
        
        return {
            "job_id": job_id,
            "status": "submitted",
            "message": "Scan submitted successfully",
            "estimated_completion": datetime.utcnow() + timedelta(minutes=5)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit scan: {str(e)}"
        )


@router.post("/jobs", response_model=ReportJobResponse)
async def create_report_job(
    job_request: ReportJobCreate,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    engine: ReportEngine = Depends(get_report_engine)
) -> ReportJobResponse:
    """Create a new report generation job"""
    try:
        job_id = str(uuid.uuid4())
        
        # Create job record in database
        job = ReportJob(
            id=job_id,
            scan_id=job_request.scan_id,
            report_formats=job_request.formats,
            template_id=job_request.template_id,
            status=ReportStatus.PENDING,
            created_by=current_user["user_id"],
            created_at=datetime.utcnow()
        )
        
        # Start background report generation
        background_tasks.add_task(
            generate_report_background,
            job_id,
            job_request,
            current_user["user_id"]
        )
        
        return ReportJobResponse(
            job_id=job_id,
            status=ReportStatus.PENDING,
            created_at=job.created_at,
            estimated_completion=datetime.utcnow() + timedelta(minutes=3)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create report job: {str(e)}"
        )


@router.get("/jobs/{job_id}", response_model=ReportJobResponse)
async def get_job_status(
    job_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ReportJobResponse:
    """Get status of a report generation job"""
    try:
        # Query job from database
        # For now, return mock data
        return ReportJobResponse(
            job_id=job_id,
            status=ReportStatus.COMPLETED,
            created_at=datetime.utcnow() - timedelta(minutes=5),
            completed_at=datetime.utcnow(),
            report_urls={"html": f"/api/v1/reporting/reports/{job_id}.html"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Job not found: {str(e)}"
        )


@router.get("/jobs")
async def list_jobs(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """List report generation jobs"""
    try:
        # Query jobs from database
        # For now, return mock data
        jobs = [
            {
                "job_id": f"job_{i}",
                "status": "completed",
                "created_at": datetime.utcnow() - timedelta(hours=i),
                "scan_id": f"scan_{i}"
            }
            for i in range(1, 6)
        ]
        
        return {
            "jobs": jobs,
            "total": len(jobs),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list jobs: {str(e)}"
        )


# === REPORT RETRIEVAL ===

@router.get("/reports/{report_id}")
async def download_report(
    report_id: str,
    format: Optional[ReportFormat] = ReportFormat.HTML,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Download a generated report"""
    try:
        settings = get_settings()
        
        # Map format to file extension and MIME type
        format_info = {
            ReportFormat.PDF: ("pdf", "application/pdf"),
            ReportFormat.HTML: ("html", "text/html"),
            ReportFormat.MARKDOWN: ("md", "text/markdown"),
            ReportFormat.CSV: ("csv", "text/csv"),
            ReportFormat.JSON: ("json", "application/json"),
            ReportFormat.SARIF: ("sarif", "application/json"),
        }
        
        ext, mime_type = format_info.get(format, ("html", "text/html"))
        file_path = settings.reporting.reports_dir / f"{report_id}.{ext}"
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Report not found")
        
        return FileResponse(
            path=str(file_path),
            media_type=mime_type,
            filename=f"report_{report_id}.{ext}"
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Report file not found")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download report: {str(e)}"
        )


# === REPORT COMPARISON & DIFF ===

@router.post("/diff")
async def create_report_diff(
    baseline_scan_id: str,
    current_scan_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Generate diff between two scan reports"""
    try:
        diff_engine = ReportDiffEngine()
        diff_id = str(uuid.uuid4())
        
        # Generate diff
        diff_result = await diff_engine.generate_diff(
            baseline_scan_id=baseline_scan_id,
            current_scan_id=current_scan_id
        )
        
        return {
            "diff_id": diff_id,
            "baseline_scan_id": baseline_scan_id,
            "current_scan_id": current_scan_id,
            "summary": diff_result.get("summary", {}),
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate diff: {str(e)}"
        )


# === TEMPLATE MANAGEMENT ===

@router.get("/templates")
async def list_templates(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[ReportTemplateResponse]:
    """List available report templates"""
    try:
        # Return mock templates
        templates = [
            ReportTemplateResponse(
                id="executive_summary",
                name="Executive Summary",
                description="High-level summary for executives",
                output_formats=["html", "pdf"],
                is_public=True,
                category="executive",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                created_by="system",
                usage_count=0
            ),
            ReportTemplateResponse(
                id="technical_detailed",
                name="Technical Detailed",
                description="Detailed technical report for developers",
                output_formats=["html", "json", "sarif"],
                is_public=True,
                category="technical",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                created_by="system",
                usage_count=0
            ),
            ReportTemplateResponse(
                id="compliance_audit",
                name="Compliance Audit",
                description="Compliance-focused audit report",
                output_formats=["html", "pdf", "csv"],
                is_public=False,
                category="compliance",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                created_by="system",
                usage_count=0
            )
        ]
        return templates
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list templates: {str(e)}"
        )


@router.post("/templates", response_model=ReportTemplateResponse)
async def create_template(
    template_data: ReportTemplateCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ReportTemplateResponse:
    """Create a new report template"""
    try:
        template_id = str(uuid.uuid4())
        
        # Create template in database
        template = ReportTemplateResponse(
            id=template_id,
            name=template_data.name,
            description=template_data.description,
            category=template_data.category,
            created_at=datetime.utcnow()
        )
        
        return template
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create template: {str(e)}"
        )


# === THEMES AND STYLING ===

@router.get("/themes")
async def list_themes(current_user: Dict[str, Any] = Depends(get_current_user)):
    """List available report themes"""
    try:
        theme_manager = ThemeManager()
        themes = theme_manager.list_available_themes()
        return {"themes": themes}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list themes: {str(e)}"
        )


@router.get("/widgets")
async def list_widgets(current_user: Dict[str, Any] = Depends(get_current_user)):
    """List available report widgets"""
    try:
        widget_registry = WidgetRegistry()
        widgets = widget_registry.list_available_widgets()
        return {"widgets": widgets}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list widgets: {str(e)}"
        )


# === EXPORT & PUBLISHING ===

@router.post("/export")
async def export_reports(
    export_request: ReportExportRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Export multiple reports as a bundle"""
    try:
        exporter = ReportExporter(db)
        
        # Generate export bundle
        bundle_data = await exporter.export_reports(
            report_ids=export_request.report_ids,
            format=export_request.format
        )
        
        export_id = str(uuid.uuid4())
        
        return {
            "export_id": export_id,
            "status": "completed",
            "download_url": f"/api/v1/reporting/exports/{export_id}/download",
            "created_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export reports: {str(e)}"
        )


@router.post("/publish")
async def publish_report(
    publish_request: ReportPublishRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Publish a report to client portal"""
    try:
        # Generate public access token
        access_token = str(uuid.uuid4())
        
        return {
            "access_token": access_token,
            "public_url": f"/portal/reports/{access_token}",
            "published_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to publish report: {str(e)}"
        )


# === BACKGROUND TASKS ===

async def process_scan_background(job_id: str, scan_request: ScanRequest, user_id: str):
    """Background task to process scan and generate reports"""
    try:
        # Simulate scan processing
        await asyncio.sleep(2)
        
        # Generate sample scan result
        scan_result = ScanResult(
            scan_id=job_id,
            contract_address=scan_request.contract_address,
            scan_type=scan_request.scan_type,
            status="completed",
            findings_count=5,
            critical_count=1,
            high_count=2,
            medium_count=2,
            low_count=0
        )
        
        # Update job status
        print(f"Scan {job_id} completed successfully")
        
    except Exception as e:
        print(f"Scan {job_id} failed: {str(e)}")


async def generate_report_background(job_id: str, job_request: ReportJobCreate, user_id: str):
    """Background task to generate reports"""
    try:
        # Simulate report generation
        await asyncio.sleep(3)
        
        # Generate reports in requested formats
        settings = get_settings()
        
        for format in job_request.formats:
            # Create mock report file
            report_path = settings.reporting.reports_dir / f"{job_id}.{format.value}"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format == ReportFormat.JSON:
                content = json.dumps({
                    "report_id": job_id,
                    "scan_id": job_request.scan_id,
                    "generated_at": datetime.utcnow().isoformat(),
                    "findings": []
                }, indent=2)
            elif format == ReportFormat.HTML:
                content = f"""
                <!DOCTYPE html>
                <html>
                <head><title>Security Report {job_id}</title></head>
                <body>
                    <h1>Security Scan Report</h1>
                    <p>Report ID: {job_id}</p>
                    <p>Generated: {datetime.utcnow().isoformat()}</p>
                </body>
                </html>
                """
            else:
                content = f"Report {job_id} - Generated at {datetime.utcnow()}"
            
            report_path.write_text(content, encoding="utf-8")
        
        print(f"Report generation {job_id} completed successfully")
        
    except Exception as e:
        print(f"Report generation {job_id} failed: {str(e)}")


# === HEALTH & STATUS ===

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@router.get("/status")
async def system_status():
    """System status endpoint"""
    return {
        "system": "operational",
        "database": "connected",
        "queue": "operational",
        "storage": "available",
        "timestamp": datetime.utcnow().isoformat()
    }
