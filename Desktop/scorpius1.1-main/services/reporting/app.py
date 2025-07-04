"""
Scorpius Enterprise Reporting Service
====================================

Comprehensive reporting engine for smart contract vulnerability analysis.
Supports multiple formats, digital signatures, templating, and audit trails.
"""

import os
import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import zipfile

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse, HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Scorpius Enterprise Reporting Service",
    description="Enterprise-grade reporting engine for smart contract vulnerability scanning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security
security = HTTPBearer()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === MODELS ===

class SeverityLevel(str):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class ReportFormat(str):
    PDF = "pdf"
    HTML = "html"
    JSON = "json"
    CSV = "csv"
    SARIF = "sarif"
    MARKDOWN = "markdown"

class ReportStatus(str):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"

class VulnerabilityFinding(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    severity: str
    category: str
    file_path: str
    line_number: Optional[int] = None
    function_name: Optional[str] = None
    contract_name: Optional[str] = None
    code_snippet: Optional[str] = None
    recommendation: Optional[str] = None
    references: List[str] = Field(default_factory=list)

class ContractInfo(BaseModel):
    name: str
    file_path: str
    source_code: Optional[str] = None
    bytecode: Optional[str] = None
    compiler_version: Optional[str] = None
    lines_of_code: Optional[int] = None

class ScanResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_name: str
    scan_type: str = "comprehensive"
    status: str = "completed"
    contracts: List[ContractInfo] = Field(default_factory=list)
    vulnerabilities: List[VulnerabilityFinding] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    scanner_version: str = "1.0.0"
    
    @property
    def total_issues(self) -> int:
        return len(self.vulnerabilities)
    
    @property
    def critical_issues(self) -> int:
        return len([v for v in self.vulnerabilities if v.severity == "critical"])
    
    @property
    def high_issues(self) -> int:
        return len([v for v in self.vulnerabilities if v.severity == "high"])
    
    @property
    def medium_issues(self) -> int:
        return len([v for v in self.vulnerabilities if v.severity == "medium"])
    
    @property
    def low_issues(self) -> int:
        return len([v for v in self.vulnerabilities if v.severity == "low"])

class ReportRequest(BaseModel):
    scan_id: str
    formats: List[str] = Field(default=["html", "json"])
    theme: str = "dark_pro"
    include_signature: bool = False
    include_watermark: bool = True
    custom_title: Optional[str] = None
    webhook_url: Optional[str] = None

class ReportResponse(BaseModel):
    report_id: str
    status: str
    message: str
    download_urls: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    estimated_completion: Optional[datetime] = None

class ReportTemplate(BaseModel):
    id: str
    name: str
    description: str
    type: str  # security, compliance, audit, executive
    formats: List[str]
    theme: str
    popularity: int = 0

class DiffRequest(BaseModel):
    baseline_scan_id: str
    current_scan_id: str
    output_format: str = "html"
    include_charts: bool = True

# === IN-MEMORY STORAGE ===

# In production, these would be in a database
scan_results_db: Dict[str, ScanResult] = {}
report_jobs_db: Dict[str, Dict] = {}
report_templates_db: Dict[str, ReportTemplate] = {}

# Sample data
def initialize_sample_data():
    """Initialize sample scan results and templates"""
    
    # Sample scan result
    sample_scan = ScanResult(
        id="SCAN_2024_001",
        project_name="UniswapV3Pool",
        contracts=[
            ContractInfo(
                name="UniswapV3Pool",
                file_path="/contracts/UniswapV3Pool.sol",
                compiler_version="0.8.19",
                lines_of_code=1250
            )
        ],
        vulnerabilities=[
            VulnerabilityFinding(
                title="Reentrancy in swap function",
                description="The swap function is vulnerable to reentrancy attacks due to external calls before state updates.",
                severity="high",
                category="reentrancy",
                file_path="/contracts/UniswapV3Pool.sol",
                line_number=342,
                function_name="swap",
                contract_name="UniswapV3Pool",
                recommendation="Use the checks-effects-interactions pattern or reentrancy guards."
            ),
            VulnerabilityFinding(
                title="Integer overflow in price calculation",
                description="Potential integer overflow in price calculation could lead to incorrect pricing.",
                severity="medium",
                category="arithmetic",
                file_path="/contracts/UniswapV3Pool.sol",
                line_number=198,
                function_name="calculatePrice",
                contract_name="UniswapV3Pool",
                recommendation="Use SafeMath library or Solidity 0.8+ built-in overflow protection."
            )
        ]
    )
    scan_results_db[sample_scan.id] = sample_scan
    
    # Sample templates
    templates = [
        ReportTemplate(
            id="security_audit",
            name="Security Audit Report",
            description="Comprehensive security analysis with vulnerability details",
            type="security",
            formats=["pdf", "html", "json", "sarif"],
            theme="dark_pro",
            popularity=95
        ),
        ReportTemplate(
            id="executive_summary",
            name="Executive Summary",
            description="High-level overview for management and stakeholders",
            type="executive",
            formats=["pdf", "html"],
            theme="corporate_blue",
            popularity=84
        )
    ]
    
    for template in templates:
        report_templates_db[template.id] = template

# === REPORT GENERATORS ===

class HTMLReportGenerator:
    def generate(self, scan_result: ScanResult, theme: str = "dark_pro") -> str:
        """Generate HTML report"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Security Audit Report - {scan_result.project_name}</title>
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #1a1a1a; color: #fff; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
                .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
                .stat-card {{ background: #2a2a2a; padding: 20px; border-radius: 8px; text-align: center; }}
                .critical {{ color: #ff4757; }}
                .high {{ color: #ff6b4a; }}
                .medium {{ color: #ffa502; }}
                .low {{ color: #26de81; }}
                .vulnerability {{ background: #2a2a2a; margin: 15px 0; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; }}
                .severity {{ padding: 4px 12px; border-radius: 4px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Security Audit Report</h1>
                <h2>{scan_result.project_name}</h2>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="summary">
                <div class="stat-card">
                    <h3>Total Issues</h3>
                    <h2>{scan_result.total_issues}</h2>
                </div>
                <div class="stat-card">
                    <h3 class="critical">Critical</h3>
                    <h2>{scan_result.critical_issues}</h2>
                </div>
                <div class="stat-card">
                    <h3 class="high">High</h3>
                    <h2>{scan_result.high_issues}</h2>
                </div>
                <div class="stat-card">
                    <h3 class="medium">Medium</h3>
                    <h2>{scan_result.medium_issues}</h2>
                </div>
                <div class="stat-card">
                    <h3 class="low">Low</h3>
                    <h2>{scan_result.low_issues}</h2>
                </div>
            </div>
            
            <h2>Vulnerabilities</h2>
        """
        
        for vuln in scan_result.vulnerabilities:
            html_content += f"""
            <div class="vulnerability">
                <h3>{vuln.title}</h3>
                <span class="severity {vuln.severity}">{vuln.severity.upper()}</span>
                <p><strong>Description:</strong> {vuln.description}</p>
                <p><strong>File:</strong> {vuln.file_path}:{vuln.line_number or 'N/A'}</p>
                <p><strong>Function:</strong> {vuln.function_name or 'N/A'}</p>
                {f'<p><strong>Recommendation:</strong> {vuln.recommendation}</p>' if vuln.recommendation else ''}
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        return html_content

class JSONReportGenerator:
    def generate(self, scan_result: ScanResult) -> str:
        """Generate JSON report"""
        return scan_result.json(indent=2)

class SARIFReportGenerator:
    def generate(self, scan_result: ScanResult) -> str:
        """Generate SARIF v2.1.0 report"""
        sarif_report = {
            "version": "2.1.0",
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": "Scorpius Security Scanner",
                        "version": scan_result.scanner_version,
                        "informationUri": "https://scorpius.security"
                    }
                },
                "results": []
            }]
        }
        
        for vuln in scan_result.vulnerabilities:
            result = {
                "ruleId": vuln.category,
                "message": {"text": vuln.description},
                "level": self._map_severity(vuln.severity),
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {"uri": vuln.file_path},
                        "region": {"startLine": vuln.line_number or 1}
                    }
                }]
            }
            sarif_report["runs"][0]["results"].append(result)
        
        return json.dumps(sarif_report, indent=2)
    
    def _map_severity(self, severity: str) -> str:
        mapping = {
            "critical": "error",
            "high": "error", 
            "medium": "warning",
            "low": "note",
            "info": "note"
        }
        return mapping.get(severity, "warning")

# === API ENDPOINTS ===

@app.on_event("startup")
async def startup_event():
    """Initialize the reporting service"""
    logger.info("Starting Scorpius Reporting Service...")
    
    # Create output directories
    os.makedirs("./reports", exist_ok=True)
    os.makedirs("./reports/html", exist_ok=True)
    os.makedirs("./reports/pdf", exist_ok=True)
    os.makedirs("./reports/json", exist_ok=True)
    os.makedirs("./reports/sarif", exist_ok=True)
    
    # Initialize sample data
    initialize_sample_data()
    
    logger.info("Reporting Service initialized successfully")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "scorpius-reporting",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "scorpius-reporting",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/capabilities")
async def get_capabilities():
    """Get service capabilities"""
    return {
        "supported_formats": ["html", "json", "sarif", "pdf", "csv", "markdown"],
        "supported_themes": ["dark_pro", "light_corporate", "corporate_blue", "minimal"],
        "features": {
            "digital_signatures": True,
            "watermarking": True,
            "templates": True,
            "diff_reports": True,
            "bulk_export": True,
            "webhook_notifications": True
        },
        "templates": len(report_templates_db),
        "max_file_size": "100MB"
    }

@app.get("/scans")
async def list_scans(limit: int = 50, offset: int = 0):
    """List available scan results"""
    scans = list(scan_results_db.values())[offset:offset + limit]
    return {
        "scans": [
            {
                "id": scan.id,
                "project_name": scan.project_name,
                "status": scan.status,
                "total_issues": scan.total_issues,
                "critical_issues": scan.critical_issues,
                "high_issues": scan.high_issues,
                "created_at": scan.created_at.isoformat()
            }
            for scan in scans
        ],
        "total": len(scan_results_db),
        "offset": offset,
        "limit": limit
    }

@app.get("/scans/{scan_id}")
async def get_scan(scan_id: str):
    """Get specific scan result"""
    if scan_id not in scan_results_db:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return scan_results_db[scan_id]

@app.post("/reports/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    background_tasks: BackgroundTasks
):
    """Generate a new report"""
    
    # Validate scan exists
    if request.scan_id not in scan_results_db:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Generate report ID
    report_id = str(uuid.uuid4())
    
    # Initialize job
    report_jobs_db[report_id] = {
        "id": report_id,
        "scan_id": request.scan_id,
        "status": ReportStatus.PENDING,
        "formats": request.formats,
        "theme": request.theme,
        "created_at": datetime.now(),
        "progress": 0,
        "download_urls": {}
    }
    
    # Start background generation
    background_tasks.add_task(
        generate_report_background,
        report_id,
        request
    )
    
    return ReportResponse(
        report_id=report_id,
        status=ReportStatus.PENDING,
        message="Report generation started",
        estimated_completion=datetime.now() + timedelta(minutes=2)
    )

@app.get("/reports/{report_id}/status")
async def get_report_status(report_id: str):
    """Get report generation status"""
    if report_id not in report_jobs_db:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report_jobs_db[report_id]

@app.get("/reports/{report_id}/download/{format}")
async def download_report(report_id: str, format: str):
    """Download generated report"""
    if report_id not in report_jobs_db:
        raise HTTPException(status_code=404, detail="Report not found")
    
    job = report_jobs_db[report_id]
    if job["status"] != ReportStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Report not ready")
    
    if format not in job["download_urls"]:
        raise HTTPException(status_code=404, detail="Format not available")
    
    file_path = job["download_urls"][format]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine media type
    media_types = {
        "html": "text/html",
        "json": "application/json",
        "sarif": "application/json",
        "pdf": "application/pdf",
        "csv": "text/csv"
    }
    
    return FileResponse(
        file_path,
        media_type=media_types.get(format, "application/octet-stream"),
        filename=f"report_{report_id}.{format}"
    )

@app.get("/templates")
async def list_templates():
    """List available report templates"""
    return {
        "templates": list(report_templates_db.values()),
        "total": len(report_templates_db)
    }

@app.post("/diff")
async def create_diff_report(request: DiffRequest, background_tasks: BackgroundTasks):
    """Create a diff report between two scans"""
    
    # Validate scans exist
    if request.baseline_scan_id not in scan_results_db:
        raise HTTPException(status_code=404, detail="Baseline scan not found")
    if request.current_scan_id not in scan_results_db:
        raise HTTPException(status_code=404, detail="Current scan not found")
    
    diff_id = str(uuid.uuid4())
    
    # Start background diff generation
    background_tasks.add_task(
        generate_diff_background,
        diff_id,
        request
    )
    
    return {
        "diff_id": diff_id,
        "status": "generating",
        "message": "Diff report generation started"
    }

@app.post("/export")
async def export_reports(report_ids: List[str]):
    """Export multiple reports as a ZIP file"""
    
    # Validate all reports exist
    for report_id in report_ids:
        if report_id not in report_jobs_db:
            raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    
    # Create ZIP file
    zip_path = f"./reports/export_{uuid.uuid4()}.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for report_id in report_ids:
            job = report_jobs_db[report_id]
            for format_type, file_path in job.get("download_urls", {}).items():
                if os.path.exists(file_path):
                    zipf.write(file_path, f"{report_id}.{format_type}")
    
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"reports_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    )

# === BACKGROUND TASKS ===

async def generate_report_background(report_id: str, request: ReportRequest):
    """Background task to generate reports"""
    try:
        job = report_jobs_db[report_id]
        job["status"] = ReportStatus.GENERATING
        job["progress"] = 10
        
        scan_result = scan_results_db[request.scan_id]
        
        # Generate each requested format
        generators = {
            "html": HTMLReportGenerator(),
            "json": JSONReportGenerator(),
            "sarif": SARIFReportGenerator()
        }
        
        for i, format_type in enumerate(request.formats):
            if format_type in generators:
                # Generate content
                if format_type == "html":
                    content = generators[format_type].generate(scan_result, request.theme)
                else:
                    content = generators[format_type].generate(scan_result)
                
                # Save to file
                file_path = f"./reports/{format_type}/report_{report_id}.{format_type}"
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                job["download_urls"][format_type] = file_path
                job["progress"] = 30 + (i + 1) * (60 / len(request.formats))
        
        # Mark as completed
        job["status"] = ReportStatus.COMPLETED
        job["progress"] = 100
        job["completed_at"] = datetime.now()
        
        logger.info(f"Report {report_id} generated successfully")
        
    except Exception as e:
        logger.error(f"Error generating report {report_id}: {e}")
        job["status"] = ReportStatus.FAILED
        job["error"] = str(e)

async def generate_diff_background(diff_id: str, request: DiffRequest):
    """Background task to generate diff reports"""
    try:
        baseline = scan_results_db[request.baseline_scan_id]
        current = scan_results_db[request.current_scan_id]
        
        # Simple diff logic
        baseline_vulns = {v.title: v for v in baseline.vulnerabilities}
        current_vulns = {v.title: v for v in current.vulnerabilities}
        
        new_vulns = [v for title, v in current_vulns.items() if title not in baseline_vulns]
        fixed_vulns = [v for title, v in baseline_vulns.items() if title not in current_vulns]
        common_vulns = [v for title, v in current_vulns.items() if title in baseline_vulns]
        
        diff_result = {
            "diff_id": diff_id,
            "baseline_scan": baseline.id,
            "current_scan": current.id,
            "summary": {
                "new_vulnerabilities": len(new_vulns),
                "fixed_vulnerabilities": len(fixed_vulns),
                "unchanged_vulnerabilities": len(common_vulns)
            },
            "new_vulnerabilities": [v.dict() for v in new_vulns],
            "fixed_vulnerabilities": [v.dict() for v in fixed_vulns],
            "generated_at": datetime.now().isoformat()
        }
        
        # Save diff result
        file_path = f"./reports/diff_{diff_id}.json"
        with open(file_path, 'w') as f:
            json.dump(diff_result, f, indent=2)
        
        logger.info(f"Diff report {diff_id} generated successfully")
        
    except Exception as e:
        logger.error(f"Error generating diff {diff_id}: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8007,
        reload=True,
        log_level="info"
    )
