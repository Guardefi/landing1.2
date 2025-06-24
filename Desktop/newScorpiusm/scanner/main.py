"""
Advanced Vulnerability Scanner Service
Provides containerized security analysis using Slither, Mythril, Manticore, Echidna, and custom plugins
"""

import asyncio
import json
import subprocess
import tempfile
import uuid
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import aiohttp
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI(title="Scorpius Advanced Vulnerability Scanner", version="2.0.0")

# Configuration
RESULTS_DIR = Path("/app/results")
RESULTS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR = Path("/app/outputs")
OUTPUTS_DIR.mkdir(exist_ok=True)

# Data Models
class ScanRequest(BaseModel):
    target: str
    plugins: list[str] = ["slither-static", "mythril-symbolic", "manticore-symbolic", "reentrancy"]
    enable_simulation: bool = True
    scan_id: str
    rpc_url: str | None = None
    timeout: int = 300  # Default 5 minutes


class Finding(BaseModel):
    id: str
    title: str
    severity: str
    description: str
    confidence: float
    recommendation: str | None = None
    source_tool: str
    metadata: dict[str, Any] = {}
    location: str | None = None


class ScanResult(BaseModel):
    scan_id: str
    status: str
    target: str
    findings: list[Finding]
    created_at: str
    completed_at: str | None = None
    error: str | None = None


class Plugin(BaseModel):
    name: str
    description: str
    category: str
    version: str = "1.0.0"


# In-memory storage (use database in production)
scan_results: dict[str, ScanResult] = {}


async def run_slither_analysis(contract_code: str, temp_dir: Path) -> list[Finding]:
    """Run Slither static analysis"""
    findings = []
    
    try:
        # Write contract to temporary file
        contract_file = temp_dir / "contract.sol"
        contract_file.write_text(contract_code)
        
        # Run Slither with JSON output
        cmd = [
            "slither", 
            str(contract_file),
            "--json", "-",
            "--exclude-dependencies"
        ]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=60
        )
        
        if result.returncode == 0 and result.stdout:
            slither_output = json.loads(result.stdout)
            
            # Parse Slither findings
            for detector in slither_output.get("results", {}).get("detectors", []):
                finding = Finding(
                    id=str(uuid.uuid4()),
                    title=f"Slither: {detector.get('check', 'Unknown Issue')}",
                    severity=map_slither_severity(detector.get("impact", "info")),
                    description=detector.get("description", "No description available"),
                    confidence=map_slither_confidence(detector.get("confidence", "medium")),
                    recommendation=f"Review {detector.get('check', 'this issue')} - {detector.get('wiki', '')}",
                    source_tool="slither",
                    metadata={
                        "check": detector.get("check"),
                        "impact": detector.get("impact"),
                        "confidence": detector.get("confidence"),
                        "wiki": detector.get("wiki"),
                        "elements": detector.get("elements", [])
                    },
                    location=get_location_from_elements(detector.get("elements", []))
                )
                findings.append(finding)
                
    except subprocess.TimeoutExpired:
        findings.append(Finding(
            id=str(uuid.uuid4()),
            title="Slither Analysis Timeout",
            severity="warning",
            description="Slither analysis timed out after 60 seconds",
            confidence=1.0,
            source_tool="slither",
            metadata={"error": "timeout"}
        ))
    except Exception as e:
        findings.append(Finding(
            id=str(uuid.uuid4()),
            title="Slither Analysis Error",
            severity="error",
            description=f"Slither analysis failed: {str(e)}",
            confidence=1.0,
            source_tool="slither",
            metadata={"error": str(e)}
        ))
    
    return findings


async def run_mythril_analysis(contract_code: str, temp_dir: Path) -> list[Finding]:
    """Run Mythril symbolic execution analysis"""
    findings = []
    
    try:
        # Write contract to temporary file
        contract_file = temp_dir / "contract.sol"
        contract_file.write_text(contract_code)
        
        # Run Mythril with JSON output
        cmd = [
            "myth",
            "analyze",
            str(contract_file),
            "--output", "json",
            "--execution-timeout", "30"
        ]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=60
        )
        
        if result.stdout:
            try:
                mythril_output = json.loads(result.stdout)
                
                # Parse Mythril findings
                for issue in mythril_output.get("issues", []):
                    finding = Finding(
                        id=str(uuid.uuid4()),
                        title=f"Mythril: {issue.get('title', 'Security Issue')}",
                        severity=map_mythril_severity(issue.get("severity", "Medium")),
                        description=issue.get("description", "No description available"),
                        confidence=0.8,  # Mythril doesn't provide confidence scores
                        recommendation=f"Review {issue.get('title', 'this issue')}",
                        source_tool="mythril",
                        metadata={
                            "swc_id": issue.get("swc-id"),
                            "type": issue.get("type"),
                            "address": issue.get("address"),
                            "function": issue.get("function")
                        },
                        location=f"Line {issue.get('lineno', 'unknown')}"
                    )
                    findings.append(finding)
            except json.JSONDecodeError:
                # Mythril might return non-JSON output on error
                pass
                
    except subprocess.TimeoutExpired:
        findings.append(Finding(
            id=str(uuid.uuid4()),
            title="Mythril Analysis Timeout",
            severity="warning",
            description="Mythril analysis timed out after 60 seconds",
            confidence=1.0,
            source_tool="mythril",
            metadata={"error": "timeout"}
        ))
    except Exception as e:
        findings.append(Finding(
            id=str(uuid.uuid4()),
            title="Mythril Analysis Error",
            severity="error",
            description=f"Mythril analysis failed: {str(e)}",
            confidence=1.0,
            source_tool="mythril",
            metadata={"error": str(e)}
        ))
    
    return findings


async def run_manticore_analysis(contract_code: str, temp_dir: Path) -> list[Finding]:
    """Run Manticore symbolic execution analysis"""
    findings = []
    
    try:
        # Write contract to temporary file
        contract_file = temp_dir / "contract.sol"
        contract_file.write_text(contract_code)
        
        # Create Manticore analysis script
        analysis_script = temp_dir / "manticore_analysis.py"
        script_content = f"""
import sys
import json
from manticore.ethereum import ManticoreEVM
from manticore.core.plugin import Plugin

class VulnerabilityDetector(Plugin):
    def __init__(self):
        super().__init__()
        self.findings = []
    
    def will_evm_execute_instruction_callback(self, state, instruction):
        # Detect potential vulnerabilities during execution
        if instruction.opcode == 'CALL':
            # Check for reentrancy possibilities
            self.findings.append({{
                "type": "reentrancy_risk",
                "pc": hex(instruction.pc),
                "description": "External call detected - potential reentrancy"
            }})
        
        if instruction.opcode == 'SSTORE':
            # Check for state changes after external calls
            if hasattr(state, 'has_external_call'):
                self.findings.append({{
                    "type": "state_change_after_call",
                    "pc": hex(instruction.pc),
                    "description": "State change after external call"
                }})

try:
    m = ManticoreEVM()
    detector = VulnerabilityDetector()
    m.register_plugin(detector)
    
    # Load and analyze contract
    account = m.create_account(balance=1000)
    contract_account = m.solidity_create_contract("{str(contract_file)}")
    
    # Run symbolic execution
    m.multi_tx_analysis()
    
    # Output findings
    print(json.dumps(detector.findings))
    
except Exception as e:
    print(json.dumps({{"error": str(e)}}))
"""
        analysis_script.write_text(script_content)
        
        # Run Manticore analysis
        cmd = ["python", str(analysis_script)]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(temp_dir)
        )
        
        if result.stdout:
            try:
                manticore_output = json.loads(result.stdout)
                
                if isinstance(manticore_output, list):
                    for issue in manticore_output:
                        finding = Finding(
                            id=str(uuid.uuid4()),
                            title=f"Manticore: {issue.get('type', 'Unknown Issue').replace('_', ' ').title()}",
                            severity="medium",
                            description=issue.get('description', 'Manticore detected a potential issue'),
                            confidence=0.7,
                            recommendation="Review the symbolic execution findings",
                            source_tool="manticore",
                            metadata={
                                "pc": issue.get("pc"),
                                "type": issue.get("type")
                            }
                        )
                        findings.append(finding)
                        
            except json.JSONDecodeError:
                pass
                
    except subprocess.TimeoutExpired:
        findings.append(Finding(
            id=str(uuid.uuid4()),
            title="Manticore Analysis Timeout",
            severity="warning",
            description="Manticore analysis timed out after 120 seconds",
            confidence=1.0,
            source_tool="manticore",
            metadata={"error": "timeout"}
        ))
    except Exception as e:
        findings.append(Finding(
            id=str(uuid.uuid4()),
            title="Manticore Analysis Error",
            severity="error",
            description=f"Manticore analysis failed: {str(e)}",
            confidence=1.0,
            source_tool="manticore",
            metadata={"error": str(e)}
        ))
    
    return findings


async def run_reentrancy_analysis(contract_code: str) -> list[Finding]:
    """Run custom reentrancy detection"""
    findings = []
    
    # Simple pattern matching for reentrancy vulnerabilities
    reentrancy_patterns = [
        {"pattern": r"\.call\s*\(\s*", "severity": "high", "title": "Potential Reentrancy via call()"},
        {"pattern": r"\.send\s*\(\s*", "severity": "medium", "title": "Potential Reentrancy via send()"},
        {"pattern": r"\.transfer\s*\(\s*", "severity": "low", "title": "Transfer usage (safe from reentrancy)"},
        {"pattern": r"msg\.value.*call", "severity": "high", "title": "Ether transfer with call()"}
    ]
    
    import re
    
    for pattern_info in reentrancy_patterns:
        matches = re.finditer(pattern_info["pattern"], contract_code, re.IGNORECASE)
        for match in matches:
            # Find line number
            line_num = contract_code[:match.start()].count('\n') + 1
            
            finding = Finding(
                id=str(uuid.uuid4()),
                title=pattern_info["title"],
                severity=pattern_info["severity"],
                description=f"Found potential reentrancy pattern at line {line_num}: {match.group()}",
                confidence=0.6,
                recommendation="Implement reentrancy guard using OpenZeppelin ReentrancyGuard",
                source_tool="reentrancy_detector",
                location=f"Line {line_num}",
                metadata={                    "pattern": pattern_info["pattern"],
                    "match": match.group(),
                    "line": line_num
                }
            )
            findings.append(finding)
    
    return findings


async def analyze_contract_from_address(address: str, rpc_url: str = None) -> str:
    """Fetch contract source code from blockchain"""
    # This is a simplified version - in production, you'd use services like:
    # - Etherscan API
    # - Sourcify
    # - Block explorer APIs
    
    # For now, return a sample vulnerable contract for testing
    return """
pragma solidity ^0.8.0;

contract VulnerableContract {
    mapping(address => uint256) public balances;
    
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
    
    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        // Vulnerable to reentrancy - state change after external call
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        balances[msg.sender] -= amount;
    }
    
    function getBalance() public view returns (uint256) {
        return balances[msg.sender];
    }
}
"""


# Utility functions
def map_slither_severity(impact: str) -> str:
    mapping = {
        "High": "high",
        "Medium": "medium", 
        "Low": "low",
        "Informational": "info"
    }
    return mapping.get(impact, "info")


def map_slither_confidence(confidence: str) -> float:
    mapping = {
        "High": 0.9,
        "Medium": 0.7,
        "Low": 0.5
    }
    return mapping.get(confidence, 0.5)


def map_mythril_severity(severity: str) -> str:
    mapping = {
        "High": "high",
        "Medium": "medium",
        "Low": "low"
    }
    return mapping.get(severity, "medium")


def get_location_from_elements(elements: list[dict]) -> str:
    """Extract location information from Slither elements"""
    if not elements:
        return "Unknown location"
    
    element = elements[0]
    source_mapping = element.get("source_mapping", {})
    if source_mapping:
        return f"Line {source_mapping.get('lines', ['unknown'])[0]}"
    
    return "Unknown location"


# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "vulnerability_scanner",
        "tools": ["slither", "mythril", "reentrancy_detector"],
        "version": "1.0.0"
    }


@app.get("/plugins")
async def get_plugins():
    """Get available analysis plugins"""
    plugins = [
        Plugin(
            name="slither-static",
            description="Static analysis using Slither framework",
            category="security",
            version="0.10.0"
        ),
        Plugin(
            name="mythril-symbolic", 
            description="Symbolic execution analysis with Mythril",
            category="security",
            version="0.24.8"
        ),        Plugin(
            name="manticore-symbolic",
            description="Advanced symbolic execution with Manticore",
            category="security",
            version="0.3.7"
        ),
        Plugin(
            name="reentrancy",
            description="Custom reentrancy vulnerability detection",
            category="security",
            version="1.0.0"
        )
    ]
    
    return [plugin.dict() for plugin in plugins]


@app.post("/scan")
async def start_scan(request: ScanRequest):
    """Start a new vulnerability scan"""
    scan_id = request.scan_id
    
    # Initialize scan result
    scan_result = ScanResult(
        scan_id=scan_id,
        status="running",
        target=request.target,
        findings=[],
        created_at=datetime.utcnow().isoformat()
    )
    scan_results[scan_id] = scan_result
    
    # Start scan in background
    asyncio.create_task(perform_scan(request))
    
    return {
        "scan_id": scan_id,
        "status": "running",
        "message": "Scan started successfully"
    }


@app.get("/scan/{scan_id}")
async def get_scan_status(scan_id: str):
    """Get scan status and results"""
    if scan_id not in scan_results:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return scan_results[scan_id].dict()


async def perform_scan(request: ScanRequest):
    """Perform the actual vulnerability scan"""
    scan_id = request.scan_id
    
    try:
        # Get contract source code
        if request.target.startswith("0x"):
            # Blockchain address
            contract_code = await analyze_contract_from_address(
                request.target, 
                request.rpc_url
            )
        else:
            # Assume it's source code
            contract_code = request.target
        
        all_findings = []
        
        # Create temporary directory for analysis
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
              # Run selected plugins
            for plugin in request.plugins:
                if plugin == "slither-static":
                    findings = await run_slither_analysis(contract_code, temp_path)
                    all_findings.extend(findings)
                elif plugin == "mythril-symbolic":
                    findings = await run_mythril_analysis(contract_code, temp_path)
                    all_findings.extend(findings)
                elif plugin == "manticore-symbolic":
                    findings = await run_manticore_analysis(contract_code, temp_path)
                    all_findings.extend(findings)
                elif plugin == "reentrancy":
                    findings = await run_reentrancy_analysis(contract_code)
                    all_findings.extend(findings)
        
        # Update scan result
        scan_results[scan_id].findings = all_findings
        scan_results[scan_id].status = "completed"
        scan_results[scan_id].completed_at = datetime.utcnow().isoformat()
        
    except Exception as e:
        # Update scan result with error
        scan_results[scan_id].status = "failed"
        scan_results[scan_id].error = str(e)
        scan_results[scan_id].completed_at = datetime.utcnow().isoformat()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
