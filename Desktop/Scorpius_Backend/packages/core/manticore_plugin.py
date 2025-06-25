"""Manticore scanner plugin for Scorpius Vulnerability Scanner

This module integrates the Manticore symbolic execution engine for smart contract analysis.
Manticore is a symbolic execution tool that can find vulnerabilities in Ethereum smart contracts
by exploring execution paths and detecting security issues.
"""

import json
import logging
import os
import subprocess
import tempfile
import asyncio
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set

from scanners.base import BaseScannerPlugin
from core.models import (
    ScanType, Target, ScanConfig, VulnerabilityFinding,
    VulnerabilityLevel
)

logger = logging.getLogger("scorpius.scanners.manticore")

# Mapping of Manticore detector levels to our vulnerability levels
MANTICORE_LEVEL_TO_SEVERITY = {
    "CRITICAL": VulnerabilityLevel.CRITICAL,
    "HIGH": VulnerabilityLevel.HIGH,
    "MEDIUM": VulnerabilityLevel.MEDIUM,
    "LOW": VulnerabilityLevel.LOW,
    "INFORMATIONAL": VulnerabilityLevel.INFO,
    "OPTIMIZATION": VulnerabilityLevel.INFO
}


class ManticorePlugin(BaseScannerPlugin):
    """Manticore symbolic execution plugin for smart contract security analysis"""
    
    NAME = "manticore"
    DESCRIPTION = "Deep symbolic execution analysis of smart contracts using Manticore"
    VERSION = "0.1.0"
    AUTHOR = "Scorpius Team"
    SUPPORTED_SCAN_TYPES = [ScanType.DYNAMIC, ScanType.FULL, ScanType.DEEP]
    DEPENDENCIES = ["manticore"]
    
    def __init__(self):
        """Initialize the Manticore plugin"""
        super().__init__()
        self.temp_dirs = []
        
    async def initialize(self) -> bool:
        """Initialize the Manticore plugin
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        if self.initialized:
            return True
        
        # Call parent initialization, which checks dependencies
        if not await super().initialize():
            return False
        
        try:
            # Check if Manticore is installed and available
            proc = await asyncio.create_subprocess_exec(
                "manticore", "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                logger.error(f"Manticore is not installed or not in PATH")
                return False
                
            # Parse version to ensure compatibility
            version = stdout.decode().strip() if stdout else ""
            logger.info(f"Found Manticore version: {version}")
            
            self.initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Manticore plugin: {e}")
            return False
    
    async def _check_dependency(self, dependency: str) -> bool:
        """Check if a specific dependency is available
        
        Args:
            dependency: The dependency to check
            
        Returns:
            bool: True if dependency is available, False otherwise
        """
        if dependency == "manticore":
            try:
                # Use pip to check if it's installed
                proc = await asyncio.create_subprocess_exec(
                    "pip", "show", "manticore",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()
                return proc.returncode == 0
            except Exception:
                return False
                
        return await super()._check_dependency(dependency)
    
    async def scan(self, target: Target, config: ScanConfig) -> List[VulnerabilityFinding]:
        """Perform a security scan using Manticore
        
        Args:
            target: Target to scan
            config: Configuration for the scan
            
        Returns:
            List[VulnerabilityFinding]: List of vulnerability findings
        """
        if not self.initialized:
            await self.initialize()
            if not self.initialized:
                logger.error("Cannot perform scan, Manticore plugin not initialized")
                return []
        
        logger.info(f"Starting Manticore scan for target {target.identifier}")
        
        # Manticore can analyze:
        # 1. Solidity source files
        # 2. Bytecode
        
        if target.source_code:
            return await self._scan_source_files(target, config)
        elif target.bytecode:
            return await self._scan_bytecode(target, config)
        else:
            logger.error("Target does not provide source code or bytecode")
            return []
    
    async def _scan_source_files(self, target: Target, config: ScanConfig) -> List[VulnerabilityFinding]:
        """Scan Solidity source files with Manticore
        
        Args:
            target: Target with source code
            config: Scan configuration
            
        Returns:
            List[VulnerabilityFinding]: List of findings
        """
        # Create a temporary directory to save the source files
        temp_dir = tempfile.mkdtemp(prefix="manticore_scan_")
        self.temp_dirs.append(temp_dir)
        
        try:
            # Source code can be a dict of file paths to content or a single string
            if isinstance(target.source_code, dict):
                # Write each source file to the temporary directory
                for filename, content in target.source_code.items():
                    file_path = os.path.join(temp_dir, filename)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'w') as f:
                        f.write(content)
                
                # Find the main contract file (usually the one with the contract name)
                main_file = next(
                    (f for f in target.source_code.keys() if target.name in f),
                    next(iter(target.source_code.keys()))
                )
                main_file_path = os.path.join(temp_dir, main_file)
            else:
                # Single source file
                main_file = f"{target.name if target.name else 'contract'}.sol"
                main_file_path = os.path.join(temp_dir, main_file)
                with open(main_file_path, 'w') as f:
                    f.write(str(target.source_code))
            
            # Run Manticore on the source code
            return await self._run_manticore(main_file_path, target, config)
            
        except Exception as e:
            logger.error(f"Error scanning source files with Manticore: {e}")
            return []
        finally:
            # Clean up
            await self._cleanup_temp_dir(temp_dir)
    
    async def _scan_bytecode(self, target: Target, config: ScanConfig) -> List[VulnerabilityFinding]:
        """Scan contract bytecode with Manticore
        
        Args:
            target: Target with bytecode
            config: Scan configuration
            
        Returns:
            List[VulnerabilityFinding]: List of findings
        """
        logger.info("Scanning contract bytecode with Manticore")
        
        try:
            # Output directory
            temp_dir = tempfile.mkdtemp(prefix="manticore_bytecode_scan_")
            self.temp_dirs.append(temp_dir)
            
            # Save bytecode to a file
            bytecode_file = os.path.join(temp_dir, "bytecode.evm")
            with open(bytecode_file, 'w') as f:
                f.write(target.bytecode if not target.bytecode.startswith('0x') else target.bytecode[2:])
                
            # Build Manticore command for bytecode
            cmd = [
                "manticore",
                "--core.procs", str(os.cpu_count() or 2),
                "--", bytecode_file
            ]
            
            # For deep scans, run with more resources
            if config.scan_type == ScanType.DEEP:
                cmd.extend(["--core.timeout", str(config.timeout * 2)])
            else:
                cmd.extend(["--core.timeout", str(config.timeout)])
                
            # Execute Manticore
            logger.info(f"Running Manticore on bytecode: {' '.join(cmd)}")
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=temp_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            stdout_str = stdout.decode() if stdout else ""
            stderr_str = stderr.decode() if stderr else ""
            
            if proc.returncode != 0:
                logger.error(f"Manticore failed with error: {stderr_str}")
                return []
            
            # Manticore output directory
            manticore_output_dir = os.path.join(temp_dir, "mcore_*")
            import glob
            output_dirs = glob.glob(manticore_output_dir)
            
            if not output_dirs:
                logger.warning("Manticore did not create any output directory")
                return []
                
            # Parse results from the output directory
            return await self._parse_manticore_output(output_dirs[0], target, config)
            
        except Exception as e:
            logger.error(f"Error scanning bytecode with Manticore: {e}")
            return []
        finally:
            # Clean up
            await self._cleanup_temp_dir(temp_dir)
    
    async def _run_manticore(self, file_path: str, target: Target, config: ScanConfig) -> List[VulnerabilityFinding]:
        """Run Manticore on a Solidity file
        
        Args:
            file_path: Path to the Solidity file
            target: Scan target
            config: Scan configuration
            
        Returns:
            List[VulnerabilityFinding]: List of findings
        """
        try:
            # Build Manticore command
            cmd = [
                "manticore", 
                file_path,
                "--solc-solcs-bin", config.custom_options.get("solc_path", "/usr/bin/solc"),
                "--core.procs", str(os.cpu_count() or 2),
                "--detect-all"
            ]
            
            # For deep scans, run with more thorough checks
            if config.scan_type == ScanType.DEEP:
                cmd.extend(["--core.timeout", str(config.timeout * 2)])
            else:
                cmd.extend(["--core.timeout", str(config.timeout)])
                
            # Working directory is the directory of the file
            working_dir = os.path.dirname(file_path)
            
            # Execute Manticore
            logger.info(f"Running Manticore: {' '.join(cmd)}")
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=working_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            stdout_str = stdout.decode() if stdout else ""
            stderr_str = stderr.decode() if stderr else ""
            
            if proc.returncode != 0:
                logger.error(f"Manticore failed with error: {stderr_str}")
                return []
            
            # Manticore output directory
            manticore_output_dir = os.path.join(working_dir, "mcore_*")
            import glob
            output_dirs = glob.glob(manticore_output_dir)
            
            if not output_dirs:
                logger.warning("Manticore did not create any output directory")
                return []
                
            # Parse results from the output directory
            return await self._parse_manticore_output(output_dirs[0], target, config)
                
        except Exception as e:
            logger.error(f"Error running Manticore: {e}")
            return []
    
    async def _parse_manticore_output(self, output_dir: str, target: Target, config: ScanConfig) -> List[VulnerabilityFinding]:
        """Parse Manticore output into VulnerabilityFinding objects
        
        Args:
            output_dir: Path to the Manticore output directory
            target: Scan target
            config: Scan configuration
            
        Returns:
            List[VulnerabilityFinding]: List of parsed vulnerability findings
        """
        findings = []
        
        try:
            # Check for global.findings.json file
            findings_file = os.path.join(output_dir, "global.findings.json")
            if not os.path.exists(findings_file):
                logger.warning(f"No findings file found in {output_dir}")
                return []
                
            with open(findings_file, 'r') as f:
                manticore_findings = json.load(f)
                
            # Process each finding
            for finding in manticore_findings:
                # Skip findings without a title
                if not finding.get("title"):
                    continue
                    
                # Map Manticore severity to our severity levels
                severity_str = finding.get("type", "INFORMATIONAL").upper()
                severity = MANTICORE_LEVEL_TO_SEVERITY.get(severity_str, VulnerabilityLevel.MEDIUM)
                
                # Generate a unique ID for this finding
                finding_id = f"MANTICORE-{uuid.uuid4()}"
                
                # Extract location information
                location = finding.get("filename", "unknown")
                line_number = finding.get("lineno")
                snippet = finding.get("code")
                
                # Create finding object
                vulnerability_finding = VulnerabilityFinding(
                    id=finding_id,
                    vulnerability_type=finding.get("title", "Unknown Vulnerability"),
                    title=finding.get("title", "Unknown Vulnerability"),
                    description=finding.get("description", "No description provided"),
                    severity=severity,
                    confidence=0.7,  # Manticore doesn't provide confidence, use a fixed value
                    location=location,
                    line_number=line_number,
                    snippet=snippet,
                    source="manticore",
                    recommendation=finding.get("recommendation"),
                    cwe_id=finding.get("swc_id"),
                    tags=["symbolic-execution", "dynamic-analysis", "evm", 
                          finding.get("title", "").lower().replace(" ", "-")],
                    metadata={"manticore_raw": finding}
                )
                
                findings.append(vulnerability_finding)
                
            logger.info(f"Manticore found {len(findings)} issues")
            return findings
                
        except Exception as e:
            logger.error(f"Error parsing Manticore output: {e}")
            return []
    
    async def _cleanup_temp_dir(self, temp_dir: str) -> None:
        """Clean up a temporary directory
        
        Args:
            temp_dir: Path to the temporary directory
        """
        if os.path.exists(temp_dir):
            try:
                import shutil
                shutil.rmtree(temp_dir)
                if temp_dir in self.temp_dirs:
                    self.temp_dirs.remove(temp_dir)
                logger.debug(f"Removed temporary directory: {temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary directory {temp_dir}: {e}")
    
    async def cleanup(self) -> None:
        """Clean up resources used by the plugin"""
        await super().cleanup()
        
        # Clean up any remaining temporary directories
        for temp_dir in list(self.temp_dirs):
            await self._cleanup_temp_dir(temp_dir)
