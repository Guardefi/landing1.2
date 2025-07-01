"""
Immutable Audit Trail Service
FastAPI service for cryptographically signed audit logging
"""

import csv
import hashlib
import io
import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .core.auth import User, get_current_user
from .core.config import settings
from .models import AuditExportRequest, AuditExportResponse, AuditQuery, AuditRecord
from .services.audit_store import AuditStore
from .services.signature_service import SignatureService

app = FastAPI(
    title="Scorpius Audit Trail",
    description="Immutable audit trail and compliance logging service",
    version="1.0.0",
    docs_url="/audit/docs" if settings.DEBUG else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Initialize services
audit_store = AuditStore()
signature_service = SignatureService()


@app.get("/audit/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "audit-trail",
        "version": "1.0.0",
        "timestamp": time.time(),
    }


@app.post("/audit/log")
async def log_audit_record(record: AuditRecord, user: User = Depends(get_current_user)):
    """Log an audit record to the immutable trail"""
    try:
        # Add metadata
        record.timestamp = time.time()
        record.logged_by = user.id
        record.org_id = user.org_id

        # Generate content hash
        content = {
            "event_type": record.event_type,
            "resource_id": record.resource_id,
            "action": record.action,
            "details": record.details,
            "timestamp": record.timestamp,
            "user_id": record.user_id,
            "org_id": record.org_id,
        }
        record.content_hash = hashlib.sha256(
            json.dumps(content, sort_keys=True).encode()
        ).hexdigest()

        # Sign the record
        record.signature = await signature_service.sign_record(record)

        # Store in audit trail
        record_id = await audit_store.store_record(record)

        return {
            "record_id": record_id,
            "content_hash": record.content_hash,
            "signature": record.signature,
            "timestamp": record.timestamp,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to log audit record: {str(e)}"
        )


@app.get("/audit/records")
async def get_audit_records(
    org_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0),
    user: User = Depends(get_current_user),
):
    """Get audit records with filtering"""
    try:
        # Build query
        query = AuditQuery(
            org_id=org_id or user.org_id,
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )

        # Fetch records
        records = await audit_store.query_records(query)

        return {
            "records": records,
            "total": len(records),
            "offset": offset,
            "limit": limit,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to query audit records: {str(e)}"
        )


@app.post("/audit/export")
async def export_audit_records(
    request: AuditExportRequest, user: User = Depends(get_current_user)
):
    """Export audit records as signed CSV"""
    try:
        # Query records for export
        query = AuditQuery(
            org_id=request.org_id or user.org_id,
            event_type=request.event_type,
            start_date=request.start_date,
            end_date=request.end_date,
            limit=10000,  # Max export limit
        )

        records = await audit_store.query_records(query)

        # Generate CSV
        csv_data = await generate_csv_export(records)

        # Generate SHA-256 signature for the CSV
        csv_hash = hashlib.sha256(csv_data.encode()).hexdigest()
        signature = await signature_service.sign_data(csv_data.encode())

        # Store export record
        export_record = AuditRecord(
            event_type="audit_export",
            resource_id=f"export_{int(time.time())}",
            action="export",
            user_id=user.id,
            details={
                "records_count": len(records),
                "csv_hash": csv_hash,
                "export_signature": signature,
            },
        )
        await audit_store.store_record(export_record)

        return AuditExportResponse(
            csv_data=csv_data,
            record_count=len(records),
            export_hash=csv_hash,
            signature=signature,
            exported_at=time.time(),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to export audit records: {str(e)}"
        )


@app.get("/audit/verify/{record_id}")
async def verify_audit_record(record_id: str, user: User = Depends(get_current_user)):
    """Verify the integrity of an audit record"""
    try:
        # Fetch record
        record = await audit_store.get_record(record_id)
        if not record:
            raise HTTPException(status_code=404, detail="Audit record not found")

        # Verify signature
        is_valid = await signature_service.verify_record(record)

        return {
            "record_id": record_id,
            "is_valid": is_valid,
            "content_hash": record.content_hash,
            "signature": record.signature,
            "verified_at": time.time(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to verify audit record: {str(e)}"
        )


async def generate_csv_export(records: List[Dict[str, Any]]) -> str:
    """Generate CSV export from audit records"""
    output = io.StringIO()

    if not records:
        return ""

    # Define CSV columns
    fieldnames = [
        "timestamp",
        "event_type",
        "resource_id",
        "action",
        "user_id",
        "org_id",
        "content_hash",
        "signature",
        "details",
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for record in records:
        # Convert details to JSON string
        record_copy = record.copy()
        if "details" in record_copy and isinstance(record_copy["details"], dict):
            record_copy["details"] = json.dumps(record_copy["details"])

        writer.writerow(record_copy)

    return output.getvalue()


if __name__ == "__main__":
    uvicorn.run(
        "app:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG
    )
