"""
Scorpius Enterprise Platform - Signed PDF & SARIF Reporting Service
Advanced reporting microservice with cryptographic signatures and audit trails
"""

import os
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from uuid import uuid4
import hashlib
import hmac
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
import uvicorn
from pydantic import BaseModel, Field, validator
import aiofiles
import httpx

from core.config import get_settings
from core.auth import verify_api_key
from services.pdf_generator import PDFGenerator
from services.sarif_generator import SARIFGenerator
from services.signature_service import SignatureService
from services.audit_service import AuditService
from services.qldb_service import QLDBService
from models import (
    ReportRequest, ReportResponse, PDFReportRequest, SARIFReportRequest,
    ReportStatus, SignatureInfo, AuditEntry
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Scorpius Reporting Service",
    description="Enterprise-grade signed PDF and SARIF reporting with cryptographic integrity",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security
security = HTTPBearer()
settings = get_settings()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services
pdf_generator = PDFGenerator()
sarif_generator = SARIFGenerator()
signature_service = SignatureService()
audit_service = AuditService()
qldb_service = QLDBService()

# In-memory report status tracking (in production, use Redis)
report_status_cache: Dict[str, Dict] = {}


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Scorpius Reporting Service...")
    
    # Initialize services
    await signature_service.initialize()
    await qldb_service.initialize()
    await audit_service.initialize()
    
    # Ensure output directories exist
    os.makedirs("./reports/pdf", exist_ok=True)
    os.makedirs("./reports/sarif", exist_ok=True)
    os.makedirs("./reports/signed", exist_ok=True)
    
    logger.info("Reporting Service initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Reporting Service...")
    await signature_service.cleanup()
    await qldb_service.cleanup()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "reporting",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    # In production, integrate with prometheus_client
    return {
        "reports_generated_total": 0,
        "signatures_created_total": 0,
        "audit_entries_total": 0,
        "service_uptime_seconds": 0
    }


@app.post("/v1/reports/pdf", response_model=ReportResponse)
async def generate_pdf_report(
    request: PDFReportRequest,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Generate a signed PDF report"""
    
    # Verify API key
    api_key_data = await verify_api_key(credentials.credentials)
    if not api_key_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Generate report ID
    report_id = str(uuid4())
    
    # Initialize report status
    report_status_cache[report_id] = {
        "status": ReportStatus.PROCESSING,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "report_type": "pdf",
        "user_id": api_key_data.get("user_id"),
        "progress": 0
    }
    
    # Start background processing
    background_tasks.add_task(
        process_pdf_report,
        report_id,
        request,
        api_key_data
    )
    
    logger.info(f"PDF report generation started: {report_id}")
    
    return ReportResponse(
        report_id=report_id,
        status=ReportStatus.PROCESSING,
        message="PDF report generation started",
        estimated_completion=datetime.now(timezone.utc).isoformat()
    )


@app.post("/v1/reports/sarif", response_model=ReportResponse)
async def generate_sarif_report(
    request: SARIFReportRequest,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Generate a signed SARIF report"""
    
    # Verify API key
    api_key_data = await verify_api_key(credentials.credentials)
    if not api_key_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Generate report ID
    report_id = str(uuid4())
    
    # Initialize report status
    report_status_cache[report_id] = {
        "status": ReportStatus.PROCESSING,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "report_type": "sarif",
        "user_id": api_key_data.get("user_id"),
        "progress": 0
    }
    
    # Start background processing
    background_tasks.add_task(
        process_sarif_report,
        report_id,
        request,
        api_key_data
    )
    
    logger.info(f"SARIF report generation started: {report_id}")
    
    return ReportResponse(
        report_id=report_id,
        status=ReportStatus.PROCESSING,
        message="SARIF report generation started",
        estimated_completion=datetime.now(timezone.utc).isoformat()
    )


@app.get("/v1/reports/{report_id}/status")
async def get_report_status(
    report_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get report generation status"""
    
    # Verify API key
    api_key_data = await verify_api_key(credentials.credentials)
    if not api_key_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    if report_id not in report_status_cache:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    report_status = report_status_cache[report_id]
    
    # Check if user has access to this report
    if report_status.get("user_id") != api_key_data.get("user_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return report_status


@app.get("/v1/reports/{report_id}/download")
async def download_report(
    report_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Download a completed report"""
    
    # Verify API key
    api_key_data = await verify_api_key(credentials.credentials)
    if not api_key_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    if report_id not in report_status_cache:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    report_status = report_status_cache[report_id]
    
    # Check if user has access to this report
    if report_status.get("user_id") != api_key_data.get("user_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Check if report is ready
    if report_status["status"] != ReportStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Report not ready. Status: {report_status['status']}"
        )
    
    # Get file path
    file_path = report_status.get("file_path")
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found"
        )
    
    # Log download
    await audit_service.log_event(
        event_type="report_download",
        user_id=api_key_data.get("user_id"),
        details={
            "report_id": report_id,
            "report_type": report_status["report_type"]
        }
    )
    
    # Return file
    filename = os.path.basename(file_path)
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )


@app.get("/v1/reports/{report_id}/signature")
async def get_report_signature(
    report_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get cryptographic signature information for a report"""
    
    # Verify API key
    api_key_data = await verify_api_key(credentials.credentials)
    if not api_key_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    if report_id not in report_status_cache:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    report_status = report_status_cache[report_id]
    
    # Check if user has access to this report
    if report_status.get("user_id") != api_key_data.get("user_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get signature info
    signature_info = report_status.get("signature_info")
    if not signature_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signature information not available"
        )
    
    return signature_info


async def process_pdf_report(report_id: str, request: PDFReportRequest, api_key_data: Dict):
    """Background task to process PDF report generation"""
    try:
        logger.info(f"Processing PDF report: {report_id}")
        
        # Update progress
        report_status_cache[report_id]["progress"] = 10
        report_status_cache[report_id]["message"] = "Generating PDF content..."
        
        # Generate PDF
        pdf_content = await pdf_generator.generate_report(
            title=request.title,
            data=request.data,
            template=request.template,
            metadata=request.metadata
        )
        
        # Update progress
        report_status_cache[report_id]["progress"] = 50
        report_status_cache[report_id]["message"] = "Signing PDF..."
        
        # Sign PDF
        signed_pdf = await signature_service.sign_pdf(
            pdf_content=pdf_content,
            signer_id=api_key_data.get("user_id"),
            metadata={
                "report_id": report_id,
                "generation_time": datetime.now(timezone.utc).isoformat(),
                "service": "scorpius-reporting"
            }
        )
        
        # Update progress
        report_status_cache[report_id]["progress"] = 70
        report_status_cache[report_id]["message"] = "Storing in QLDB..."
        
        # Store hash in QLDB
        pdf_hash = hashlib.sha256(signed_pdf).hexdigest()
        qldb_doc_id = await qldb_service.store_document_hash(
            document_id=report_id,
            document_hash=pdf_hash,
            document_type="signed_pdf_report",
            metadata={
                "title": request.title,
                "user_id": api_key_data.get("user_id"),
                "generation_time": datetime.now(timezone.utc).isoformat()
            }
        )
        
        # Update progress
        report_status_cache[report_id]["progress"] = 90
        report_status_cache[report_id]["message"] = "Finalizing..."
        
        # Save signed PDF to file
        file_path = f"./reports/signed/pdf_{report_id}.pdf"
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(signed_pdf)
        
        # Create audit entry
        await audit_service.log_event(
            event_type="pdf_report_generated",
            user_id=api_key_data.get("user_id"),
            details={
                "report_id": report_id,
                "file_hash": pdf_hash,
                "qldb_doc_id": qldb_doc_id,
                "file_size": len(signed_pdf)
            }
        )
        
        # Update final status
        report_status_cache[report_id].update({
            "status": ReportStatus.COMPLETED,
            "progress": 100,
            "message": "PDF report generated successfully",
            "file_path": file_path,
            "file_hash": pdf_hash,
            "qldb_doc_id": qldb_doc_id,
            "signature_info": {
                "algorithm": "RSA-SHA256",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "certificate_fingerprint": await signature_service.get_cert_fingerprint()
            },
            "completed_at": datetime.now(timezone.utc).isoformat()
        })
        
        logger.info(f"PDF report completed: {report_id}")
        
    except Exception as e:
        logger.error(f"Error processing PDF report {report_id}: {str(e)}")
        report_status_cache[report_id].update({
            "status": ReportStatus.FAILED,
            "message": f"Error: {str(e)}",
            "failed_at": datetime.now(timezone.utc).isoformat()
        })


async def process_sarif_report(report_id: str, request: SARIFReportRequest, api_key_data: Dict):
    """Background task to process SARIF report generation"""
    try:
        logger.info(f"Processing SARIF report: {report_id}")
        
        # Update progress
        report_status_cache[report_id]["progress"] = 10
        report_status_cache[report_id]["message"] = "Generating SARIF content..."
        
        # Generate SARIF
        sarif_content = await sarif_generator.generate_report(
            scan_results=request.scan_results,
            tool_info=request.tool_info,
            run_metadata=request.run_metadata
        )
        
        # Update progress
        report_status_cache[report_id]["progress"] = 40
        report_status_cache[report_id]["message"] = "Signing SARIF..."
        
        # Sign SARIF
        signed_sarif = await signature_service.sign_json(
            json_content=sarif_content,
            signer_id=api_key_data.get("user_id"),
            metadata={
                "report_id": report_id,
                "generation_time": datetime.now(timezone.utc).isoformat(),
                "service": "scorpius-reporting"
            }
        )
        
        # Update progress
        report_status_cache[report_id]["progress"] = 70
        report_status_cache[report_id]["message"] = "Storing in QLDB..."
        
        # Store hash in QLDB
        sarif_hash = hashlib.sha256(json.dumps(signed_sarif).encode()).hexdigest()
        qldb_doc_id = await qldb_service.store_document_hash(
            document_id=report_id,
            document_hash=sarif_hash,
            document_type="signed_sarif_report",
            metadata={
                "tool": request.tool_info.get("name", "unknown"),
                "user_id": api_key_data.get("user_id"),
                "generation_time": datetime.now(timezone.utc).isoformat()
            }
        )
        
        # Update progress
        report_status_cache[report_id]["progress"] = 90
        report_status_cache[report_id]["message"] = "Finalizing..."
        
        # Save signed SARIF to file
        file_path = f"./reports/signed/sarif_{report_id}.json"
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(json.dumps(signed_sarif, indent=2))
        
        # Create audit entry
        await audit_service.log_event(
            event_type="sarif_report_generated",
            user_id=api_key_data.get("user_id"),
            details={
                "report_id": report_id,
                "file_hash": sarif_hash,
                "qldb_doc_id": qldb_doc_id,
                "file_size": len(json.dumps(signed_sarif))
            }
        )
        
        # Update final status
        report_status_cache[report_id].update({
            "status": ReportStatus.COMPLETED,
            "progress": 100,
            "message": "SARIF report generated successfully",
            "file_path": file_path,
            "file_hash": sarif_hash,
            "qldb_doc_id": qldb_doc_id,
            "signature_info": {
                "algorithm": "RSA-SHA256",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "certificate_fingerprint": await signature_service.get_cert_fingerprint()
            },
            "completed_at": datetime.now(timezone.utc).isoformat()
        })
        
        logger.info(f"SARIF report completed: {report_id}")
        
    except Exception as e:
        logger.error(f"Error processing SARIF report {report_id}: {str(e)}")
        report_status_cache[report_id].update({
            "status": ReportStatus.FAILED,
            "message": f"Error: {str(e)}",
            "failed_at": datetime.now(timezone.utc).isoformat()
        })


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8007,
        reload=True,
        log_level="info"
    )
