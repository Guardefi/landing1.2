"""
Results and Simulation API Service
Comprehensive REST API for managing scan results, simulations, and reports
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

# Configure logging
logger = logging.getLogger("scorpius.results")

# Create router
router = APIRouter()


# Pydantic models
class ScanResultSummary(BaseModel):
    scan_id: str
    target_identifier: str
    scan_type: str
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[float]
    findings_count: int
    high_severity_count: int
    medium_severity_count: int
    low_severity_count: int


class FindingDetail(BaseModel):
    id: str
    title: str
    category: str
    severity: str
    confidence: float
    description: str
    location: Dict[str, Any]
    plugin: str
    affected_functions: List[str]
    raw_output: Optional[Dict[str, Any]]


class ScanResultDetail(BaseModel):
    scan_id: str
    target: Dict[str, Any]
    scan_type: str
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[float]
    findings: List[FindingDetail]
    metadata: Dict[str, Any]
    plugin_results: Dict[str, Any]


class SimulationRequest(BaseModel):
    vulnerability_id: str
    target_identifier: str
    simulation_type: str = "proof_of_concept"
    parameters: Optional[Dict[str, Any]] = {}


class SimulationResult(BaseModel):
    simulation_id: str
    vulnerability_id: str
    status: str
    simulation_type: str
    start_time: datetime
    end_time: Optional[datetime]
    success: bool
    exploit_scenario: Optional[str]
    impact_assessment: Optional[Dict[str, Any]]
    artifacts: List[str]
    logs: List[str]


class ReportRequest(BaseModel):
    scan_id: str
    format: str = "html"  # html, pdf, json, markdown
    include_details: bool = True
    include_source_code: bool = False


# In-memory storage (replace with database in production)
scan_results_storage: Dict[str, Dict[str, Any]] = {}
simulation_results_storage: Dict[str, Dict[str, Any]] = {}


@router.get("/results", response_model=List[ScanResultSummary])
async def list_scan_results(
    status: Optional[str] = Query(None, description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by minimum severity"),
    plugin: Optional[str] = Query(None, description="Filter by plugin"),
    limit: int = Query(50, description="Maximum number of results"),
    offset: int = Query(0, description="Offset for pagination"),
):
    """List scan results with filtering and pagination"""
    try:
        results = []
        all_scans = list(scan_results_storage.values())

        # Apply filters
        filtered_scans = all_scans
        if status:
            filtered_scans = [s for s in filtered_scans if s.get("status") == status]
        if plugin:
            filtered_scans = [
                s
                for s in filtered_scans
                if any(f.get("plugin") == plugin for f in s.get("findings", []))
            ]

        # Apply pagination
        paginated_scans = filtered_scans[offset : offset + limit]

        # Convert to summary format
        for scan in paginated_scans:
            findings = scan.get("findings", [])
            high_count = len([f for f in findings if f.get("severity") == "high"])
            medium_count = len([f for f in findings if f.get("severity") == "medium"])
            low_count = len([f for f in findings if f.get("severity") == "low"])

            results.append(
                ScanResultSummary(
                    scan_id=scan["scan_id"],
                    target_identifier=scan.get("target", {}).get(
                        "identifier", "unknown"
                    ),
                    scan_type=scan.get("scan_type", "unknown"),
                    status=scan.get("status", "unknown"),
                    start_time=scan.get("start_time", datetime.now()),
                    end_time=scan.get("end_time"),
                    duration=scan.get("duration"),
                    findings_count=len(findings),
                    high_severity_count=high_count,
                    medium_severity_count=medium_count,
                    low_severity_count=low_count,
                )
            )

        return results

    except Exception as e:
        logger.error(f"Error listing scan results: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to list scan results: {str(e)}"
        )


@router.get("/results/{scan_id}", response_model=ScanResultDetail)
async def get_scan_result(scan_id: str):
    """Get detailed scan result by ID"""
    try:
        if scan_id not in scan_results_storage:
            raise HTTPException(
                status_code=404, detail=f"Scan result {scan_id} not found"
            )

        scan_data = scan_results_storage[scan_id]

        # Convert findings to detailed format
        findings = []
        for f in scan_data.get("findings", []):
            findings.append(
                FindingDetail(
                    id=f.get("id", "unknown"),
                    title=f.get("title", "Unknown"),
                    category=f.get("category", "unknown"),
                    severity=f.get("severity", "low"),
                    confidence=f.get("confidence", 0.5),
                    description=f.get("description", ""),
                    location=f.get("location", {}),
                    plugin=f.get("plugin", "unknown"),
                    affected_functions=f.get("affected_functions", []),
                    raw_output=f.get("raw_output"),
                )
            )

        return ScanResultDetail(
            scan_id=scan_id,
            target=scan_data.get("target", {}),
            scan_type=scan_data.get("scan_type", "unknown"),
            status=scan_data.get("status", "unknown"),
            start_time=scan_data.get("start_time", datetime.now()),
            end_time=scan_data.get("end_time"),
            duration=scan_data.get("duration"),
            findings=findings,
            metadata=scan_data.get("metadata", {}),
            plugin_results=scan_data.get("plugin_results", {}),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scan result: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get scan result: {str(e)}"
        )


@router.delete("/results/{scan_id}")
async def delete_scan_result(scan_id: str):
    """Delete scan result by ID"""
    try:
        if scan_id not in scan_results_storage:
            raise HTTPException(
                status_code=404, detail=f"Scan result {scan_id} not found"
            )

        del scan_results_storage[scan_id]
        return {"message": f"Scan result {scan_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting scan result: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete scan result: {str(e)}"
        )


@router.post("/simulations", response_model=Dict[str, Any])
async def start_simulation(request: SimulationRequest):
    """Start a new vulnerability simulation"""
    try:
        import uuid

        simulation_id = str(uuid.uuid4())

        # Validate vulnerability exists
        vulnerability_found = False
        for scan_data in scan_results_storage.values():
            for finding in scan_data.get("findings", []):
                if finding.get("id") == request.vulnerability_id:
                    vulnerability_found = True
                    break
            if vulnerability_found:
                break

        if not vulnerability_found:
            raise HTTPException(
                status_code=404,
                detail=f"Vulnerability {request.vulnerability_id} not found",
            )

        # Store simulation metadata
        simulation_results_storage[simulation_id] = {
            "simulation_id": simulation_id,
            "vulnerability_id": request.vulnerability_id,
            "target_identifier": request.target_identifier,
            "simulation_type": request.simulation_type,
            "status": "running",
            "start_time": datetime.now(),
            "parameters": request.parameters,
            "success": False,
            "logs": [f"Simulation {simulation_id} started"],
            "artifacts": [],
        }

        # Start simulation in background (simplified for demo)
        import asyncio

        asyncio.create_task(run_simulation(simulation_id, request))

        return {
            "simulation_id": simulation_id,
            "status": "started",
            "message": f"Simulation {simulation_id} started successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting simulation: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to start simulation: {str(e)}"
        )


@router.get("/simulations", response_model=List[Dict[str, Any]])
async def list_simulations(
    status: Optional[str] = Query(None, description="Filter by status"),
    simulation_type: Optional[str] = Query(
        None, description="Filter by simulation type"
    ),
    limit: int = Query(50, description="Maximum number of results"),
    offset: int = Query(0, description="Offset for pagination"),
):
    """List simulations with filtering and pagination"""
    try:
        simulations = list(simulation_results_storage.values())

        # Apply filters
        if status:
            simulations = [s for s in simulations if s.get("status") == status]
        if simulation_type:
            simulations = [
                s for s in simulations if s.get("simulation_type") == simulation_type
            ]

        # Apply pagination
        paginated_simulations = simulations[offset : offset + limit]

        return paginated_simulations

    except Exception as e:
        logger.error(f"Error listing simulations: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to list simulations: {str(e)}"
        )


@router.get("/simulations/{simulation_id}", response_model=SimulationResult)
async def get_simulation_result(simulation_id: str):
    """Get simulation result by ID"""
    try:
        if simulation_id not in simulation_results_storage:
            raise HTTPException(
                status_code=404, detail=f"Simulation {simulation_id} not found"
            )

        sim_data = simulation_results_storage[simulation_id]

        return SimulationResult(
            simulation_id=simulation_id,
            vulnerability_id=sim_data.get("vulnerability_id", "unknown"),
            status=sim_data.get("status", "unknown"),
            simulation_type=sim_data.get("simulation_type", "unknown"),
            start_time=sim_data.get("start_time", datetime.now()),
            end_time=sim_data.get("end_time"),
            success=sim_data.get("success", False),
            exploit_scenario=sim_data.get("exploit_scenario"),
            impact_assessment=sim_data.get("impact_assessment"),
            artifacts=sim_data.get("artifacts", []),
            logs=sim_data.get("logs", []),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting simulation result: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get simulation result: {
                str(e)}",
        )


@router.delete("/simulations/{simulation_id}")
async def delete_simulation(simulation_id: str):
    """Delete simulation by ID"""
    try:
        if simulation_id not in simulation_results_storage:
            raise HTTPException(
                status_code=404, detail=f"Simulation {simulation_id} not found"
            )

        del simulation_results_storage[simulation_id]
        return {"message": f"Simulation {simulation_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting simulation: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete simulation: {str(e)}"
        )


@router.post("/reports")
async def generate_report(request: ReportRequest):
    """Generate scan report in specified format"""
    try:
        if request.scan_id not in scan_results_storage:
            raise HTTPException(
                status_code=404,
                detail=f"Scan result {
                    request.scan_id} not found",
            )

        scan_data = scan_results_storage[request.scan_id]

        # Generate report based on format
        if request.format == "json":
            report_content = json.dumps(scan_data, indent=2, default=str)
            content_type = "application/json"
        elif request.format == "html":
            report_content = generate_html_report(scan_data, request.include_details)
            content_type = "text/html"
        elif request.format == "markdown":
            report_content = generate_markdown_report(
                scan_data, request.include_details
            )
            content_type = "text/markdown"
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported report format: {
                    request.format}",
            )

        return {
            "scan_id": request.scan_id,
            "format": request.format,
            "content_type": content_type,
            "content": report_content,
            "generated_at": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate report: {str(e)}"
        )


@router.get("/analytics/summary")
async def get_analytics_summary():
    """Get analytics summary across all scans"""
    try:
        total_scans = len(scan_results_storage)
        total_simulations = len(simulation_results_storage)

        # Calculate findings by severity
        all_findings = []
        for scan_data in scan_results_storage.values():
            all_findings.extend(scan_data.get("findings", []))

        severity_counts = {
            "high": len([f for f in all_findings if f.get("severity") == "high"]),
            "medium": len([f for f in all_findings if f.get("severity") == "medium"]),
            "low": len([f for f in all_findings if f.get("severity") == "low"]),
        }

        # Calculate plugin usage
        plugin_counts = {}
        for finding in all_findings:
            plugin = finding.get("plugin", "unknown")
            plugin_counts[plugin] = plugin_counts.get(plugin, 0) + 1

        # Calculate scan status distribution
        status_counts = {}
        for scan_data in scan_results_storage.values():
            status = scan_data.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "total_scans": total_scans,
            "total_simulations": total_simulations,
            "total_findings": len(all_findings),
            "severity_distribution": severity_counts,
            "plugin_usage": plugin_counts,
            "scan_status_distribution": status_counts,
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting analytics summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analytics summary: {
                str(e)}",
        )


async def run_simulation(simulation_id: str, request: SimulationRequest):
    """Run simulation in background (simplified implementation)"""
    try:
        import asyncio

        await asyncio.sleep(5)  # Simulate processing time

        # Update simulation with results
        simulation_results_storage[simulation_id].update(
            {
                "status": "completed",
                "end_time": datetime.now(),
                "success": True,
                "exploit_scenario": f"Simulated exploit for vulnerability {
                    request.vulnerability_id}",
                "impact_assessment": {
                    "severity": "high",
                    "financial_impact": "moderate",
                    "availability_impact": "low",
                },
                "artifacts": [
                    f"exploit_{simulation_id}.sol",
                    f"test_{simulation_id}.js",
                ],
                "logs": [
                    f"Simulation {simulation_id} started",
                    "Loading vulnerability context...",
                    "Setting up test environment...",
                    "Executing exploit scenario...",
                    "Collecting results...",
                    f"Simulation {simulation_id} completed successfully",
                ],
            }
        )

        logger.info(f"Simulation {simulation_id} completed successfully")

    except Exception as e:
        # Update simulation with error
        simulation_results_storage[simulation_id].update(
            {
                "status": "error",
                "end_time": datetime.now(),
                "success": False,
                "logs": simulation_results_storage[simulation_id]["logs"]
                + [f"Error: {str(e)}"],
            }
        )
        logger.error(f"Simulation {simulation_id} failed: {e}")


def generate_html_report(scan_data: Dict[str, Any], include_details: bool) -> str:
    """Generate HTML report"""
    findings = scan_data.get("findings", [])

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Scorpius Vulnerability Report - {scan_data.get('scan_id', 'Unknown')}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
            .finding {{ margin: 15px 0; padding: 15px; border-left: 4px solid #ccc; }}
            .finding.high {{ border-left-color: #dc3545; }}
            .finding.medium {{ border-left-color: #ffc107; }}
            .finding.low {{ border-left-color: #28a745; }}
            .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
            .stat {{ background: #e9ecef; padding: 15px; border-radius: 5px; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Vulnerability Scan Report</h1>
            <p><strong>Scan ID:</strong> {scan_data.get('scan_id', 'Unknown')}</p>
            <p><strong>Target:</strong> {scan_data.get('target', {}).get('identifier', 'Unknown')}</p>
            <p><strong>Scan Type:</strong> {scan_data.get('scan_type', 'Unknown')}</p>
            <p><strong>Status:</strong> {scan_data.get('status', 'Unknown')}</p>
            <p><strong>Generated:</strong> {datetime.now().isoformat()}</p>
        </div>

        <div class="summary">
            <div class="stat">
                <h3>{len(findings)}</h3>
                <p>Total Findings</p>
            </div>
            <div class="stat">
                <h3>{len([f for f in findings if f.get('severity') == 'high'])}</h3>
                <p>High Severity</p>
            </div>
            <div class="stat">
                <h3>{len([f for f in findings if f.get('severity') == 'medium'])}</h3>
                <p>Medium Severity</p>
            </div>
            <div class="stat">
                <h3>{len([f for f in findings if f.get('severity') == 'low'])}</h3>
                <p>Low Severity</p>
            </div>
        </div>

        <h2>Findings</h2>
    """

    for finding in findings:
        severity = finding.get("severity", "low")
        html += f"""
        <div class="finding {severity}">
            <h3>{finding.get('title', 'Unknown')}</h3>
            <p><strong>Severity:</strong> {severity.title()}</p>
            <p><strong>Plugin:</strong> {finding.get('plugin', 'Unknown')}</p>
            <p><strong>Category:</strong> {finding.get('category', 'Unknown')}</p>
            <p><strong>Confidence:</strong> {finding.get('confidence', 0.5):.1%}</p>
            <p>{finding.get('description', 'No description available')}</p>
        </div>
        """

    html += """
    </body>
    </html>
    """

    return html


def generate_markdown_report(scan_data: Dict[str, Any], include_details: bool) -> str:
    """Generate Markdown report"""
    findings = scan_data.get("findings", [])

    markdown = f"""# Vulnerability Scan Report

**Scan ID:** {scan_data.get('scan_id', 'Unknown')}
**Target:** {scan_data.get('target', {}).get('identifier', 'Unknown')}
**Scan Type:** {scan_data.get('scan_type', 'Unknown')}
**Status:** {scan_data.get('status', 'Unknown')}
**Generated:** {datetime.now().isoformat()}

## Summary

- **Total Findings:** {len(findings)}
- **High Severity:** {len([f for f in findings if f.get('severity') == 'high'])}
- **Medium Severity:** {len([f for f in findings if f.get('severity') == 'medium'])}
- **Low Severity:** {len([f for f in findings if f.get('severity') == 'low'])}

## Findings

"""

    for i, finding in enumerate(findings, 1):
        severity = finding.get("severity", "low")
        markdown += f"""
### {i}. {finding.get('title', 'Unknown')} ({severity.title()})

- **Plugin:** {finding.get('plugin', 'Unknown')}
- **Category:** {finding.get('category', 'Unknown')}
- **Confidence:** {finding.get('confidence', 0.5):.1%}

{finding.get('description', 'No description available')}

---

"""

    return markdown


# Store scan result helper function
def store_scan_result(scan_id: str, scan_data: Dict[str, Any]):
    """Store scan result in memory (replace with database in production)"""
    scan_results_storage[scan_id] = scan_data
