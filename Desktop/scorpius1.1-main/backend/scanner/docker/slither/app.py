#!/usr/bin/env python3
"""
Slither Plugin REST API Service
Standalone FastAPI service for the Slither static analysis plugin
"""

import asyncio
import json
import logging
import os
import tempfile
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("slither.api")

# Initialize FastAPI application
app = FastAPI(
    title="Slither Plugin API",
    description="Slither static analysis plugin REST API service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class ScanRequest(BaseModel):
    target_path: str
    options: Optional[Dict[str, Any]] = {}


class ScanResponse(BaseModel):
    scan_id: str
    status: str
    message: str


class AnalysisResult(BaseModel):
    scan_id: str
    status: str
    findings: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    version: str
    plugin: str


# In-memory storage for scan results
scan_results: Dict[str, Dict[str, Any]] = {}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy", version="1.0.0", plugin="slither")


@app.get("/capabilities")
async def get_capabilities():
    """Get plugin capabilities"""
    return {
        "name": "slither",
        "version": "1.0.0",
        "description": "Slither static analysis framework for Solidity",
        "supported_languages": ["solidity"],
        "scan_types": ["static"],
        "output_formats": ["json", "sarif"],
        "vulnerabilities": [
            "reentrancy",
            "arithmetic",
            "uninitialized-state",
            "locked-ether",
            "assembly",
            "low-level-calls",
            "naming-convention",
            "pragma",
            "solc-version",
            "external-function",
            "public-vs-external",
            "boolean-equal",
            "incorrect-equality",
            "tautology",
            "boolean-cst",
            "too-many-digits",
            "unused-return",
            "costly-loop",
            "dead-code",
            "redundant-statements",
        ],
    }


@app.post("/scan", response_model=ScanResponse)
async def start_scan(request: ScanRequest):
    """Start a new Slither scan"""
    try:
        import uuid

        scan_id = str(uuid.uuid4())

        # Validate target path
        if not os.path.exists(request.target_path):
            raise HTTPException(
                status_code=400,
                detail=f"Target path does not exist: {request.target_path}",
            )

        # Store scan metadata
        scan_results[scan_id] = {
            "status": "running",
            "target_path": request.target_path,
            "options": request.options,
            "findings": [],
            "metadata": {},
        }

        # Run scan in background
        asyncio.create_task(
            run_slither_scan(scan_id, request.target_path, request.options)
        )

        return ScanResponse(
            scan_id=scan_id,
            status="started",
            message=f"Slither scan {scan_id} started successfully",
        )

    except Exception as e:
        logger.error(f"Error starting scan: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start scan: {str(e)}")


@app.post("/scan/upload", response_model=ScanResponse)
async def scan_upload(file: UploadFile = File(...), options: str = Form("{}")):
    """Upload and scan a Solidity file"""
    try:
        import uuid

        scan_id = str(uuid.uuid4())

        # Parse options
        try:
            options_dict = json.loads(options)
        except json.JSONDecodeError:
            options_dict = {}

        # Save uploaded file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".sol", delete=False
        ) as tmp_file:
            content = await file.read()
            tmp_file.write(content.decode("utf-8"))
            tmp_file_path = tmp_file.name

        # Store scan metadata
        scan_results[scan_id] = {
            "status": "running",
            "target_path": tmp_file_path,
            "options": options_dict,
            "findings": [],
            "metadata": {"original_filename": file.filename},
        }

        # Run scan in background
        asyncio.create_task(run_slither_scan(scan_id, tmp_file_path, options_dict))

        return ScanResponse(
            scan_id=scan_id,
            status="started",
            message=f"Slither scan {scan_id} started for uploaded file {file.filename}",
        )

    except Exception as e:
        logger.error(f"Error starting upload scan: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to start upload scan: {str(e)}"
        )


@app.get("/scan/{scan_id}/status")
async def get_scan_status(scan_id: str):
    """Get scan status"""
    if scan_id not in scan_results:
        raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found")

    result = scan_results[scan_id]
    return {
        "scan_id": scan_id,
        "status": result["status"],
        "target_path": result["target_path"],
        "findings_count": len(result["findings"]),
        "metadata": result["metadata"],
    }


@app.get("/scan/{scan_id}/results", response_model=AnalysisResult)
async def get_scan_results(scan_id: str):
    """Get scan results"""
    if scan_id not in scan_results:
        raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found")

    result = scan_results[scan_id]
    return AnalysisResult(
        scan_id=scan_id,
        status=result["status"],
        findings=result["findings"],
        metadata=result["metadata"],
    )


@app.delete("/scan/{scan_id}")
async def delete_scan(scan_id: str):
    """Delete scan results"""
    if scan_id not in scan_results:
        raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found")

    # Clean up temporary files if they exist
    result = scan_results[scan_id]
    target_path = result.get("target_path")
    if target_path and target_path.startswith("/tmp/") and os.path.exists(target_path):
        try:
            os.unlink(target_path)
        except OSError:
            pass

    del scan_results[scan_id]
    return {"message": f"Scan {scan_id} deleted successfully"}


@app.get("/scans")
async def list_scans():
    """List all scans"""
    return {
        "scans": [
            {
                "scan_id": scan_id,
                "status": result["status"],
                "target_path": result["target_path"],
                "findings_count": len(result["findings"]),
            }
            for scan_id, result in scan_results.items()
        ]
    }


async def run_slither_scan(scan_id: str, target_path: str, options: Dict[str, Any]):
    """Run Slither scan in background"""
    try:
        logger.info(f"Starting Slither scan {scan_id} for {target_path}")

        # Build Slither command
        cmd = ["slither", target_path, "--json", "-"]

        # Add custom options
        if options.get("exclude_informational"):
            cmd.extend(["--exclude-informational"])
        if options.get("exclude_low"):
            cmd.extend(["--exclude-low"])
        if options.get("exclude_medium"):
            cmd.extend(["--exclude-medium"])
        if options.get("exclude_high"):
            cmd.extend(["--exclude-high"])

        # Run Slither
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0 or stdout:
            # Parse JSON output
            try:
                output = json.loads(stdout.decode())
                findings = []

                # Parse Slither results
                if "results" in output and "detectors" in output["results"]:
                    for detector in output["results"]["detectors"]:
                        finding = {
                            "id": f"slither-{detector.get('check', 'unknown')}",
                            "title": detector.get("description", "Unknown issue"),
                            "category": detector.get("check", "unknown"),
                            "severity": map_slither_impact(
                                detector.get("impact", "Low")
                            ),
                            "confidence": map_slither_confidence(
                                detector.get("confidence", "Medium")
                            ),
                            "description": detector.get("description", ""),
                            "location": extract_location(detector.get("elements", [])),
                            "plugin": "slither",
                            "raw_output": detector,
                        }
                        findings.append(finding)

                # Update scan results
                scan_results[scan_id].update(
                    {
                        "status": "completed",
                        "findings": findings,
                        "metadata": {
                            **scan_results[scan_id]["metadata"],
                            "slither_version": output.get("version", "unknown"),
                            "detectors_run": len(
                                output.get("results", {}).get("detectors", [])
                            ),
                            "compilation_success": True,
                        },
                    }
                )

                logger.info(
                    f"Slither scan {scan_id} completed with {len(findings)} findings"
                )

            except json.JSONDecodeError:
                # Handle non-JSON output
                scan_results[scan_id].update(
                    {
                        "status": "error",
                        "metadata": {
                            **scan_results[scan_id]["metadata"],
                            "error": "Failed to parse Slither output",
                            "raw_output": stdout.decode(),
                        },
                    }
                )
                logger.error(f"Slither scan {scan_id} failed to parse output")
        else:
            # Handle error
            scan_results[scan_id].update(
                {
                    "status": "error",
                    "metadata": {
                        **scan_results[scan_id]["metadata"],
                        "error": stderr.decode(),
                        "return_code": process.returncode,
                    },
                }
            )
            logger.error(
                f"Slither scan {scan_id} failed with return code {process.returncode}"
            )

    except Exception as e:
        scan_results[scan_id].update(
            {
                "status": "error",
                "metadata": {**scan_results[scan_id]["metadata"], "error": str(e)},
            }
        )
        logger.error(f"Slither scan {scan_id} failed with exception: {e}")


def map_slither_impact(impact: str) -> str:
    """Map Slither impact to severity"""
    mapping = {
        "High": "high",
        "Medium": "medium",
        "Low": "low",
        "Informational": "info",
    }
    return mapping.get(impact, "low")


def map_slither_confidence(confidence: str) -> float:
    """Map Slither confidence to numeric value"""
    mapping = {"High": 0.9, "Medium": 0.7, "Low": 0.5}
    return mapping.get(confidence, 0.5)


def extract_location(elements: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract location information from Slither elements"""
    if not elements:
        return {}

    element = elements[0]
    source_mapping = element.get("source_mapping", {})

    return {
        "filename": source_mapping.get("filename_short", "unknown"),
        "line": source_mapping.get("lines", [0])[0]
        if source_mapping.get("lines")
        else 0,
        "column": source_mapping.get("starting_column", 0),
        "length": source_mapping.get("length", 0),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
